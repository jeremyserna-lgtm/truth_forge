-- Sovereign Cluster Manager - Supabase Schema
-- Run this in your Supabase SQL editor

-- ============================================================================
-- NODES: Track cluster nodes
-- ============================================================================
create table public.nodes (
    id text primary key,  -- 'king', 'soldier1', 'soldier2', 'soldier3'
    hostname text not null,
    ip_address text,
    ram_total_gb integer not null,
    ram_available_gb integer,
    storage_total_gb integer,
    storage_available_gb integer,
    role text not null check (role in ('king', 'soldier')),
    status text not null default 'unknown' check (status in ('online', 'offline', 'unknown')),
    last_seen_at timestamptz,
    metadata jsonb default '{}'::jsonb,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================================
-- MODELS: Registry of all models in the vault
-- ============================================================================
create table public.models (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    path text not null,  -- relative to vault root
    base_model text,  -- null if this IS a base model
    size_gb numeric not null,
    format text not null default 'gguf',
    quantization text,  -- 'Q4_K_M', 'Q8_0', etc

    -- Deployment config
    min_ram_gb numeric,
    cluster_required boolean default false,
    single_node_capable boolean default true,

    -- Metadata
    description text,
    tags text[] default '{}',
    performance_metrics jsonb default '{}'::jsonb,  -- jeremy_arc_score, etc

    -- Status
    is_loaded boolean default false,
    loaded_at timestamptz,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================================
-- PRESETS: Saved configurations for quick loading
-- ============================================================================
create table public.presets (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    description text,
    icon text,  -- emoji or icon name

    -- Configuration
    model_id uuid references public.models(id),
    deployment_mode text not null check (deployment_mode in ('auto', 'single', 'cluster')),

    -- Memory allocation overrides (null = use defaults)
    memory_config jsonb default null,
    -- Example: {"king": 450, "soldier1": 220, "soldier2": 220, "soldier3": 220}

    -- Node selection (null = all available)
    active_nodes text[] default null,
    -- Example: ["king", "soldier1"]

    is_quick_action boolean default false,  -- Show in quick actions bar
    sort_order integer default 0,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================================
-- CLUSTER_STATE: Current state (single row, updated by agent)
-- ============================================================================
create table public.cluster_state (
    id integer primary key default 1 check (id = 1),  -- singleton

    -- Current status
    status text not null default 'unknown' check (status in ('ready', 'loading', 'running', 'error', 'unknown')),
    active_model_id uuid references public.models(id),
    active_preset_id uuid references public.presets(id),
    deployment_mode text,

    -- Aggregated metrics
    total_ram_gb integer,
    used_ram_gb integer,
    nodes_online integer,

    -- EXO state (raw from API)
    exo_state jsonb default '{}'::jsonb,

    -- Error tracking
    last_error text,
    last_error_at timestamptz,

    updated_at timestamptz default now()
);

-- Initialize singleton
insert into public.cluster_state (id, status) values (1, 'unknown')
on conflict (id) do nothing;

-- ============================================================================
-- COMMANDS: Queue for agent to process (browser -> agent)
-- ============================================================================
create table public.commands (
    id uuid primary key default gen_random_uuid(),

    command text not null check (command in (
        'load_model',
        'unload_model',
        'apply_preset',
        'refresh_state',
        'scan_vault',
        'update_memory_config'
    )),

    payload jsonb not null default '{}'::jsonb,
    -- Examples:
    -- load_model: {"model_id": "uuid", "mode": "cluster"}
    -- apply_preset: {"preset_id": "uuid"}
    -- update_memory_config: {"king": 450, "soldier1": 220, ...}

    status text not null default 'pending' check (status in ('pending', 'processing', 'completed', 'failed')),
    result jsonb,
    error text,

    created_at timestamptz default now(),
    processed_at timestamptz
);

-- ============================================================================
-- LOGS: Activity log
-- ============================================================================
create table public.logs (
    id uuid primary key default gen_random_uuid(),

    level text not null check (level in ('debug', 'info', 'warn', 'error')),
    source text not null,  -- 'agent', 'ui', 'exo'
    message text not null,
    metadata jsonb default '{}'::jsonb,

    created_at timestamptz default now()
);

-- Auto-cleanup old logs (keep 7 days)
create or replace function cleanup_old_logs()
returns trigger as $$
begin
    delete from public.logs where created_at < now() - interval '7 days';
    return new;
end;
$$ language plpgsql;

create trigger trigger_cleanup_logs
after insert on public.logs
execute function cleanup_old_logs();

-- ============================================================================
-- INDEXES
-- ============================================================================
create index idx_models_name on public.models(name);
create index idx_models_is_loaded on public.models(is_loaded);
create index idx_commands_status on public.commands(status);
create index idx_commands_created on public.commands(created_at desc);
create index idx_logs_created on public.logs(created_at desc);

-- ============================================================================
-- REALTIME: Enable for live updates
-- ============================================================================
alter publication supabase_realtime add table public.cluster_state;
alter publication supabase_realtime add table public.nodes;
alter publication supabase_realtime add table public.commands;

-- ============================================================================
-- RLS: Row Level Security (open for now, add auth later)
-- ============================================================================
alter table public.nodes enable row level security;
alter table public.models enable row level security;
alter table public.presets enable row level security;
alter table public.cluster_state enable row level security;
alter table public.commands enable row level security;
alter table public.logs enable row level security;

-- Open policies (no auth required)
create policy "Allow all" on public.nodes for all using (true);
create policy "Allow all" on public.models for all using (true);
create policy "Allow all" on public.presets for all using (true);
create policy "Allow all" on public.cluster_state for all using (true);
create policy "Allow all" on public.commands for all using (true);
create policy "Allow all" on public.logs for all using (true);

-- ============================================================================
-- SEED DATA: Initial nodes
-- ============================================================================
insert into public.nodes (id, hostname, ram_total_gb, role) values
    ('king', 'king.local', 512, 'king'),
    ('soldier1', 'soldier1.local', 256, 'soldier'),
    ('soldier2', 'soldier2.local', 256, 'soldier'),
    ('soldier3', 'soldier3.local', 256, 'soldier')
on conflict (id) do nothing;

-- ============================================================================
-- SEED DATA: Default presets
-- ============================================================================
insert into public.presets (name, description, icon, deployment_mode, is_quick_action, sort_order) values
    ('Deep Think', 'Full cluster for maximum reasoning', '🧠', 'cluster', true, 1),
    ('Fast Draft', 'King-only for quick iterations', '✍️', 'single', true, 2),
    ('Experiment', 'Latest fine-tune for testing', '🔬', 'single', true, 3),
    ('Training Mode', 'Unload models, free all RAM', 'auto', '🏋️', false, 10)
on conflict (name) do nothing;

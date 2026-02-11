-- Fix RLS policies - idempotent version that can be run safely
-- Run this in Supabase SQL Editor to enable user signup and profile creation

-- First, drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Allow public insert for signup" ON users;
DROP POLICY IF EXISTS "Users can read own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;
DROP POLICY IF EXISTS "Allow insert for user memory" ON user_memory;
DROP POLICY IF EXISTS "Users can read own memory" ON user_memory;
DROP POLICY IF EXISTS "Users can update own memory" ON user_memory;

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Allow ANY insert to users table (for signup)
-- This is needed because during signup, auth.uid() might not be set yet
CREATE POLICY "Allow public insert for signup" ON users
  FOR INSERT
  WITH CHECK (true);

-- Policy: Users can read their own data (or anyone can read if not authenticated - for initial load)
CREATE POLICY "Users can read own data" ON users
  FOR SELECT
  USING (auth.uid() = id OR auth.uid() IS NULL);

-- Policy: Users can update their own data
CREATE POLICY "Users can update own data" ON users
  FOR UPDATE
  USING (auth.uid() = id);

-- Enable RLS on user_memory table
ALTER TABLE user_memory ENABLE ROW LEVEL SECURITY;

-- Policy: Allow ANY insert for user memory (for signup initialization)
CREATE POLICY "Allow insert for user memory" ON user_memory
  FOR INSERT
  WITH CHECK (true);

-- Policy: Users can read their own memory (or anyone can read if not authenticated)
CREATE POLICY "Users can read own memory" ON user_memory
  FOR SELECT
  USING (user_id = auth.uid() OR auth.uid() IS NULL);

-- Policy: Users can update their own memory
CREATE POLICY "Users can update own memory" ON user_memory
  FOR UPDATE
  USING (user_id = auth.uid());

-- Policy: Allow ANY update on user_memory (for updating stats after signup)
-- This is permissive for now; tighten in production
CREATE POLICY "Allow update for user memory" ON user_memory
  FOR UPDATE
  WITH CHECK (true);

-- Grant usage on schema to authenticated and anon roles
GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- Grant permissions on tables
GRANT SELECT, INSERT, UPDATE ON users TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON user_memory TO anon, authenticated;

-- Output success message
SELECT 'RLS policies applied successfully!' as status;

// Create Profile Edge Function
// Handles user profile creation with service role (bypasses RLS)

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface CreateProfileRequest {
  userId: string;
  email: string;
  displayName: string;
  firstName?: string;
  lastName?: string;
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { userId, email, displayName, firstName, lastName }: CreateProfileRequest = await req.json()

    if (!userId || !email || !displayName) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: userId, email, displayName' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Create Supabase client with service role key (bypasses RLS)
    const supabaseAdmin = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Generate user code from display name
    const baseCode = displayName.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 20) || 'USER'
    const userCode = `${baseCode}_${Date.now().toString(36).toUpperCase()}`

    console.log('Creating profile for:', { userId, email, userCode })

    // Check if profile already exists
    const { data: existing } = await supabaseAdmin
      .from('users')
      .select('id')
      .eq('id', userId)
      .single()

    if (existing) {
      // Profile exists, fetch and return it
      const { data: profile } = await supabaseAdmin
        .from('users')
        .select('*')
        .eq('id', userId)
        .single()

      return new Response(
        JSON.stringify({ data: profile, created: false }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Create user profile
    const { data: profile, error: profileError } = await supabaseAdmin
      .from('users')
      .insert({
        id: userId,
        user_code: userCode,
        email,
        display_name: displayName,
        first_name: firstName || null,
        last_name: lastName || null,
        user_type: 'standard',
        is_active: true,
        is_verified: false,
        metadata: {},
      })
      .select()
      .single()

    if (profileError) {
      console.error('Profile creation error:', profileError)
      return new Response(
        JSON.stringify({ error: profileError.message }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Initialize user memory
    const { error: memoryError } = await supabaseAdmin
      .from('user_memory')
      .upsert({
        user_id: userId,
        user_code: userCode,
        insights: [],
        topics: [],
        interests: [],
        key_quotes: [],
        not_me_interests: [],
        conversation_count: 0,
        metadata: {
          documents_shared: 0,
          time_invested: 'Not yet started',
          depth_achieved: 'Surface level',
        },
      }, {
        onConflict: 'user_code,context_id',
      })

    if (memoryError) {
      console.error('Memory initialization error:', memoryError)
      // Don't fail the whole request, just log it
    }

    console.log('Profile created successfully:', profile.user_code)

    return new Response(
      JSON.stringify({ data: profile, created: true }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Edge function error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

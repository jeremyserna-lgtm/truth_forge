import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, Session, AuthError } from '@supabase/supabase-js';
import { supabase, isSupabaseConfigured } from '../lib/supabase';

interface UserProfile {
  id: string;
  user_code: string;
  email: string | null;
  display_name: string;
  first_name: string | null;
  last_name: string | null;
  user_type: string;
  is_active: boolean;
  is_verified: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface PortalStats {
  documentsShared: number;
  conversations: number;
  timeInvested: string;
  depthAchieved: string;
  lastSeen: string | null;
}

interface SignUpResult {
  error: AuthError | null;
  needsEmailConfirmation: boolean;
}

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  portalStats: PortalStats | null;
  session: Session | null;
  loading: boolean;
  isConfigured: boolean;
  signUp: (email: string, password: string, displayName: string, firstName?: string, lastName?: string) => Promise<SignUpResult>;
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
  updatePassword: (newPassword: string) => Promise<{ error: AuthError | null }>;
  updatePortalStats: (stats: Partial<PortalStats>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [portalStats, setPortalStats] = useState<PortalStats | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch user profile from our users table
  async function fetchProfile(userId: string) {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', userId)
        .single();

      if (error) {
        console.error('Error fetching profile:', error);
        return null;
      }

      return data as UserProfile;
    } catch (err) {
      console.error('Error fetching profile:', err);
      return null;
    }
  }

  // Fetch portal stats from user_memory table
  async function fetchPortalStats(userCode: string) {
    try {
      const { data, error } = await supabase
        .from('user_memory')
        .select('*')
        .eq('user_code', userCode)
        .single();

      if (error && error.code !== 'PGRST116') { // PGRST116 = not found
        console.error('Error fetching portal stats:', error);
        return null;
      }

      if (data) {
        return {
          documentsShared: data.metadata?.documents_shared || 0,
          conversations: data.conversation_count || 0,
          timeInvested: data.metadata?.time_invested || 'Not yet started',
          depthAchieved: data.metadata?.depth_achieved || 'Surface level',
          lastSeen: data.last_seen,
        } as PortalStats;
      }

      return {
        documentsShared: 0,
        conversations: 0,
        timeInvested: 'Not yet started',
        depthAchieved: 'Surface level',
        lastSeen: null,
      };
    } catch (err) {
      console.error('Error fetching portal stats:', err);
      return null;
    }
  }

  // Create user profile after signup
  async function createProfile(userId: string, email: string, displayName: string, firstName?: string, lastName?: string) {
    const userCode = displayName.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 20) || 'USER';
    const fullUserCode = `${userCode}_${Date.now().toString(36).toUpperCase()}`;

    console.log('Creating profile for user:', { userId, email, displayName, firstName, lastName, userCode: fullUserCode });

    try {
      const { data, error } = await supabase
        .from('users')
        .insert({
          id: userId,
          user_code: fullUserCode,
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
        .single();

      if (error) {
        console.error('Error creating profile - Supabase error:', error);
        console.error('Error details:', JSON.stringify(error, null, 2));
        return null;
      }

      console.log('Profile created successfully:', data);
      return data as UserProfile;
    } catch (err) {
      console.error('Error creating profile - Exception:', err);
      return null;
    }
  }

  // Initialize user memory record
  async function initializeUserMemory(userCode: string, userId: string) {
    try {
      const { error } = await supabase
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
        });

      if (error) {
        console.error('Error initializing user memory:', error);
      }
    } catch (err) {
      console.error('Error initializing user memory:', err);
    }
  }

  useEffect(() => {
    if (!isSupabaseConfigured) {
      setLoading(false);
      return;
    }

    // Get initial session
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);

      if (session?.user) {
        const userProfile = await fetchProfile(session.user.id);
        setProfile(userProfile);

        if (userProfile) {
          const stats = await fetchPortalStats(userProfile.user_code);
          setPortalStats(stats);
        }
      }

      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('Auth state change:', event, session?.user?.email);
      setSession(session);
      setUser(session?.user ?? null);

      if (session?.user) {
        let userProfile = await fetchProfile(session.user.id);

        // If no profile exists (user just confirmed email), create one
        if (!userProfile && event === 'SIGNED_IN') {
          const firstName = session.user.user_metadata?.first_name;
          const lastName = session.user.user_metadata?.last_name;
          const displayName = session.user.user_metadata?.display_name ||
                             (firstName && lastName ? `${firstName} ${lastName}` : null) ||
                             session.user.email?.split('@')[0] ||
                             'User';
          console.log('Creating profile for confirmed user:', session.user.email);
          userProfile = await createProfile(session.user.id, session.user.email || '', displayName, firstName, lastName);
          if (userProfile) {
            await initializeUserMemory(userProfile.user_code, session.user.id);
          }
        }

        setProfile(userProfile);

        if (userProfile) {
          const stats = await fetchPortalStats(userProfile.user_code);
          setPortalStats(stats);
        }
      } else {
        setProfile(null);
        setPortalStats(null);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const signUp = async (email: string, password: string, displayName: string, firstName?: string, lastName?: string): Promise<SignUpResult> => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          display_name: displayName,
          first_name: firstName,
          last_name: lastName,
        },
      },
    });

    if (error) {
      console.error('Signup error:', error);
      return { error, needsEmailConfirmation: false };
    }

    // Check if email confirmation is required
    // If session is null but user exists, email confirmation is needed
    const needsEmailConfirmation = data.user && !data.session;

    if (needsEmailConfirmation) {
      console.log('Email confirmation required for:', email);
      return { error: null, needsEmailConfirmation: true };
    }

    // If we have a session (email confirmation disabled), create profile immediately
    if (data.user && data.session) {
      const newProfile = await createProfile(data.user.id, email, displayName, firstName, lastName);
      if (newProfile) {
        setProfile(newProfile);
        await initializeUserMemory(newProfile.user_code, data.user.id);
        const stats = await fetchPortalStats(newProfile.user_code);
        setPortalStats(stats);
      }
    }

    return { error: null, needsEmailConfirmation: false };
  };

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    return { error };
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    setProfile(null);
    setPortalStats(null);
  };

  const resetPassword = async (email: string) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/login?reset=true`,
    });
    return { error };
  };

  const updatePassword = async (newPassword: string) => {
    const { error } = await supabase.auth.updateUser({
      password: newPassword,
    });
    return { error };
  };

  const updatePortalStats = async (stats: Partial<PortalStats>) => {
    if (!profile) return;

    const newStats = { ...portalStats, ...stats } as PortalStats;
    setPortalStats(newStats);

    try {
      await supabase
        .from('user_memory')
        .update({
          conversation_count: newStats.conversations,
          last_seen: new Date().toISOString(),
          metadata: {
            documents_shared: newStats.documentsShared,
            time_invested: newStats.timeInvested,
            depth_achieved: newStats.depthAchieved,
          },
        })
        .eq('user_code', profile.user_code);
    } catch (err) {
      console.error('Error updating portal stats:', err);
    }
  };

  const value = {
    user,
    profile,
    portalStats,
    session,
    loading,
    isConfigured: isSupabaseConfigured,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updatePassword,
    updatePortalStats,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

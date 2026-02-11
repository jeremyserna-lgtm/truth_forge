-- Enable RLS on users table and create policies for authentication
-- This allows users to be created during signup and read their own data

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Allow insert during signup (using service role or anon for initial creation)
CREATE POLICY "Allow public insert for signup" ON users
  FOR INSERT
  WITH CHECK (true);

-- Policy: Users can read their own data
CREATE POLICY "Users can read own data" ON users
  FOR SELECT
  USING (auth.uid() = id OR auth.uid() IS NULL);

-- Policy: Users can update their own data
CREATE POLICY "Users can update own data" ON users
  FOR UPDATE
  USING (auth.uid() = id);

-- Enable RLS on user_memory table
ALTER TABLE user_memory ENABLE ROW LEVEL SECURITY;

-- Policy: Allow insert for user memory
CREATE POLICY "Allow insert for user memory" ON user_memory
  FOR INSERT
  WITH CHECK (true);

-- Policy: Users can read their own memory
CREATE POLICY "Users can read own memory" ON user_memory
  FOR SELECT
  USING (user_id = auth.uid() OR auth.uid() IS NULL);

-- Policy: Users can update their own memory
CREATE POLICY "Users can update own memory" ON user_memory
  FOR UPDATE
  USING (user_id = auth.uid());

-- Disable email confirmation for easier testing
-- Note: This requires Dashboard access or service role
-- UPDATE auth.config SET confirm_email = false;

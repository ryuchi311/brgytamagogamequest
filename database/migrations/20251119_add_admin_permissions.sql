ALTER TABLE admin_users
    ADD COLUMN IF NOT EXISTS permissions TEXT,
    ADD COLUMN IF NOT EXISTS is_super_admin BOOLEAN DEFAULT false;

-- Ensure existing super admins have the flag enabled
UPDATE admin_users
SET is_super_admin = TRUE
WHERE role = 'super_admin';

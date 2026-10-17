# PostgreSQL / Supabase SQL Schema definition references
# This file serves as reference models for database tables.

USER_PREFERENCES_SCHEMA = """
CREATE TABLE public.user_preferences (
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, now()) NOT NULL,
  caption_size TEXT DEFAULT 'medium'::text NOT NULL,
  voice_type TEXT DEFAULT 'en-IN-Wavenet-B'::text NOT NULL,
  theme TEXT DEFAULT 'dark'::text NOT NULL,
  preferred_language TEXT DEFAULT 'en-US'::text NOT NULL,
  accessibility_enabled BOOLEAN DEFAULT true NOT NULL
);

-- Policies
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
"""

ANALYTICS_EVENTS_SCHEMA = """
CREATE TABLE public.analytics_events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, now()) NOT NULL,
  session_duration_seconds INTEGER NOT NULL,
  signs_detected_count INTEGER DEFAULT 0 NOT NULL,
  captions_characters_count INTEGER DEFAULT 0 NOT NULL,
  average_latency_ms INTEGER NOT NULL
);

-- Policies
ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;
"""

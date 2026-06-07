create table if not exists public.player_profiles (
  id text primary key,
  steam_account_id bigint unique,
  is_guest boolean not null default true,
  created_at text not null,
  updated_at text not null
);

create table if not exists public.sessions (
  id text primary key,
  profile_id text not null references public.player_profiles(id) on delete cascade,
  token_hash text not null unique,
  expires_at text not null,
  last_seen_at text not null,
  created_at text not null
);

create table if not exists public.steam_auth_states (
  state_hash text primary key,
  profile_id text not null references public.player_profiles(id) on delete cascade,
  return_to text not null,
  expires_at text not null
);

create table if not exists public.auth_exchanges (
  code_hash text primary key,
  profile_id text not null references public.player_profiles(id) on delete cascade,
  expires_at text not null
);

alter table public.reports add column if not exists profile_id text references public.player_profiles(id) on delete cascade;
alter table public.reports add column if not exists account_id bigint;
alter table public.reports add column if not exists role text;
alter table public.reports add column if not exists match_started_at bigint;
alter table public.reports add column if not exists patch integer;
alter table public.reports add column if not exists rank_tier integer;
alter table public.reports add column if not exists duration_minutes integer;
alter table public.reports add column if not exists deaths integer;
alter table public.reports add column if not exists last_hits integer;
alter table public.reports add column if not exists hero_damage integer;
alter table public.reports add column if not exists tower_damage integer;
alter table public.reports add column if not exists healing integer;
alter table public.reports add column if not exists kill_participation integer;

update public.reports
set
  account_id = nullif(payload::jsonb ->> 'account_id', '')::bigint,
  role = payload::jsonb ->> 'role',
  patch = nullif(regexp_replace(coalesce(payload::jsonb #>> '{comparison_context,patch}', ''), '\D', '', 'g'), '')::integer,
  duration_minutes = nullif(payload::jsonb #>> '{summary,duration_minutes}', '')::integer,
  deaths = nullif(payload::jsonb #>> '{summary,deaths}', '')::integer,
  last_hits = nullif(payload::jsonb #>> '{summary,last_hits}', '')::integer,
  hero_damage = nullif(payload::jsonb #>> '{summary,hero_damage}', '')::integer,
  tower_damage = nullif(payload::jsonb #>> '{summary,tower_damage}', '')::integer
where profile_id is null;

create table if not exists public.report_feedback (
  profile_id text not null references public.player_profiles(id) on delete cascade,
  report_id text not null references public.reports(id) on delete cascade,
  helpful boolean not null,
  reason text,
  created_at text not null,
  updated_at text not null,
  primary key (profile_id, report_id)
);

create table if not exists public.benchmark_samples (
  report_id text primary key references public.reports(id) on delete cascade,
  hero text not null,
  role text not null,
  rank_bracket integer,
  duration_bucket text not null,
  patch integer,
  metrics text not null,
  created_at text not null
);

create index if not exists reports_profile_created_idx on public.reports (profile_id, created_at desc);
create index if not exists reports_account_id_idx on public.reports (account_id);
create index if not exists sessions_token_hash_idx on public.sessions (token_hash);
create index if not exists benchmark_cohort_idx
  on public.benchmark_samples (hero, role, rank_bracket, duration_bucket, patch);

alter table public.player_profiles enable row level security;
alter table public.sessions enable row level security;
alter table public.steam_auth_states enable row level security;
alter table public.auth_exchanges enable row level security;
alter table public.report_feedback enable row level security;
alter table public.benchmark_samples enable row level security;

revoke all on table public.reports from anon, authenticated;
revoke all on table public.player_profiles from anon, authenticated;
revoke all on table public.sessions from anon, authenticated;
revoke all on table public.steam_auth_states from anon, authenticated;
revoke all on table public.auth_exchanges from anon, authenticated;
revoke all on table public.report_feedback from anon, authenticated;
revoke all on table public.benchmark_samples from anon, authenticated;

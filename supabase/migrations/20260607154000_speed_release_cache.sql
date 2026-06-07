create table if not exists public.match_cache (
  match_id bigint primary key,
  payload text not null,
  fetched_at text not null,
  updated_at text not null
);

create index if not exists reports_profile_match_player_role_idx
  on public.reports (profile_id, match_id, player_slot, role);

alter table public.match_cache enable row level security;

revoke all on table public.match_cache from anon, authenticated;

create policy "Backend only match cache"
  on public.match_cache for all to anon, authenticated
  using (false) with check (false);

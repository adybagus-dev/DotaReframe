drop index if exists public.sessions_token_hash_idx;

create index if not exists sessions_profile_id_idx on public.sessions (profile_id);
create index if not exists steam_auth_states_profile_id_idx on public.steam_auth_states (profile_id);
create index if not exists auth_exchanges_profile_id_idx on public.auth_exchanges (profile_id);
create index if not exists report_feedback_report_id_idx on public.report_feedback (report_id);

create policy "Backend only reports"
  on public.reports for all to anon, authenticated
  using (false) with check (false);

create policy "Backend only player profiles"
  on public.player_profiles for all to anon, authenticated
  using (false) with check (false);

create policy "Backend only sessions"
  on public.sessions for all to anon, authenticated
  using (false) with check (false);

create policy "Backend only Steam states"
  on public.steam_auth_states for all to anon, authenticated
  using (false) with check (false);

create policy "Backend only auth exchanges"
  on public.auth_exchanges for all to anon, authenticated
  using (false) with check (false);

create policy "Backend only report feedback"
  on public.report_feedback for all to anon, authenticated
  using (false) with check (false);

create policy "Backend only benchmark samples"
  on public.benchmark_samples for all to anon, authenticated
  using (false) with check (false);

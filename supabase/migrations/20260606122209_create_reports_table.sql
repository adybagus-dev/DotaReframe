create table public.reports (
  id text primary key,
  match_id bigint not null,
  player_slot integer not null,
  hero text not null,
  result text not null,
  created_at text not null,
  kda text not null,
  gpm integer not null,
  main_problem text not null,
  confidence text not null,
  payload text not null
);

create index reports_created_at_idx on public.reports (created_at desc);
create index reports_match_id_idx on public.reports (match_id);

alter table public.reports enable row level security;

comment on table public.reports is
  'DotaReframe coaching reports persisted by the FastAPI backend.';

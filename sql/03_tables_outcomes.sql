create table if not exists ovc.ovc_outcomes_v01 (
  block_id        text primary key references ovc.ovc_blocks_v01.1_min(block_id) on delete cascade,
  window          text not null default 'NEXT_4H',

  ref_price       double precision not null,     -- MIN.c at time of outcome calc
  mfe_up          double precision not null,     -- max favorable excursion upward (absolute or pct, choose one and lock)
  mfe_down        double precision not null,     -- excursion downward

  -- simple win condition placeholder (locked: ret > 0 is for MIN rows; outcomes can add more later)
  created_at      timestamptz not null default now()
);

#!/usr/bin/env python3
"""Recreate 2-hour operational screening from design assumptions.
IMPORTANT: filters ENGINEERING CONCEPTS, not new paper inclusion/exclusion or PRISMA counts.
"""
from pathlib import Path
import csv,json
root=Path(__file__).resolve().parent.parent
survey=json.loads((root/'scripts'/'design_inputs.json').read_text())['survey']
A=survey['transect_count']*survey['height_m']+(survey['transect_count']-1)*survey['transect_spacing_m']
A_minutes=A/survey['track_A_transit_speed_m_s']/60+survey['track_A_sensing_minutes']+survey['track_A_other_minutes']
B_minutes=survey['grid_stations']*(survey['track_B_volume_L_station']/survey['track_B_pump_actual_L_min']+survey['track_B_overhead_min_station']+survey['track_B_processing_min_station'])+survey['track_B_other_minutes']
methods=[
('Flow-cell camera + AI','Conditional','Supporting','Observed sensing volume and particle identity'),
('Portable filtration and imaging','Not live','Conditional','Processing time and particle recovery'),
('Polarised scattering','Conditional','Conditional','Plastic specificity against real suspended solids'),
('EIS / impedance cytometry','Conditional','Conditional','Volumetric throughput and electrolyte/particle separation'),
('Nile Red plus fluorescence','Not routine live','Conditional','Chemical step and waste handling'),
('Turbidity / conductivity / RGB','Auxiliary','Auxiliary','Requires proven site-specific relation to MPs'),
('FTIR / Raman','Excluded routine','Excluded routine','Specialist facility and time restriction'),
('Acoustic focusing','Supporting','Supporting','Enrichment requires downstream counting')]
out=root/'Method_Rationale'/'data'/'2h_Method_Operational_Gates.csv'
with out.open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['Concept','Track_A_disposition','Track_B_disposition','Constraint','Track_A_model_minutes','Track_B_model_minutes','Mission_deadline_minutes','Time_model_A_pass','Time_model_B_pass','Evidence_class'])
 for n,a,b,why in methods:w.writerow([n,a,b,why,round(A_minutes,2),round(B_minutes,2),survey['mission_minutes'],A_minutes<=survey['mission_minutes'],B_minutes<=survey['mission_minutes'],'Engineering screening only; method performance unverified'])
print(f'Wrote {out}, A={A_minutes:.1f} min, B={B_minutes:.1f} min')

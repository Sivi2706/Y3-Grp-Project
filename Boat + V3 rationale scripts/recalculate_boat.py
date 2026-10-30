#!/usr/bin/env python3
"""Recalculate boat payload, displacement, 2h route budget and battery scenarios.
All values in design_inputs.json are ENGINEERING ASSUMPTIONS unless otherwise noted.
No hydrodynamic motor performance claim is made.
"""
from pathlib import Path
import csv,json,math
p=Path(__file__).parent
x=json.loads((p/'design_inputs.json').read_text())
s,b=x['survey'],x['boat']
energy=b['battery_voltage_V']*b['battery_capacity_Ah']; usable=energy*b['battery_usable_fraction']
mass=sum(x['mass_kg'].values())
max_kg=1000*b['pontoon_count']*math.pi*(b['pontoon_diameter_m']/2)**2*b['pontoon_length_m']
length=s['transect_count']*s['height_m']+(s['transect_count']-1)*s['transect_spacing_m']
timeA=length/s['track_A_transit_speed_m_s']/60 + s['track_A_sensing_minutes']+s['track_A_other_minutes']
timeB=s['grid_stations']*(s['track_B_volume_L_station']/s['track_B_pump_actual_L_min']+s['track_B_overhead_min_station']+s['track_B_processing_min_station'])+s['track_B_other_minutes']
summary={'wet_mass_kg':mass,'theoretical_displacement_kg':max_kg,'working_displacement_kg':max_kg*b['max_working_displacement_fraction'],'nominal_energy_Wh':energy,'usable_energy_Wh':usable,'track_A_minutes':timeA,'track_B_minutes':timeB,'track_A_distance_m':length,'track_B_expected_particles_per_sample':s['semenyih_lit_concentration_particles_L']*s['track_B_volume_L_station']}
(p/'calculated_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
boat=p.parent/'Boat_Critical_Components'/'data';boat.mkdir(exist_ok=True)
with (boat/'payload_estimate.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Item','Estimated_mass_kg','Evidence_note']);
 for k,v in x['mass_kg'].items():w.writerow([k,v,'engineering estimate; validate after purchase'])
 w.writerow(['TOTAL',round(mass,3),'calculated'])
with (boat/'power_endurance.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Scenario','Usable_Wh','Average_power_W','Endurance_hours','Pass_2h_energy_only','Peak_current_not_checked']);
 for name,watt in x['power_scenarios_W'].items():w.writerow([name,usable,watt,round(usable/watt,2),2*watt<=usable,True])
print(json.dumps(summary,indent=2))

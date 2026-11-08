"""Independent derivations from frozen PDF operands; no book calculators imported."""
from fractions import Fraction
import json
from pathlib import Path

n=8
payload_gb=Fraction(140)
one_phase_sent=Fraction(n-1,n)*payload_gb
sent=2*one_phase_sent
received=sent
bidirectional_gbps=Fraction(900)
directional_gbps=bidirectional_gbps/2
ring_time=sent/directional_gbps
assert sent==245
assert received==245
assert sent+received==490
assert ring_time==(sent+received)/bidirectional_gbps
assert ring_time==Fraction(49,90)
assert sent/bidirectional_gbps==ring_time/2
result={
 'ring':{'ranks':n,'logical_tensor_GB':float(payload_gb),'reduce_scatter_sent_GB':float(one_phase_sent),'all_gather_sent_GB':float(one_phase_sent),'total_sent_GB':float(sent),'total_received_GB':float(received),'directional_bandwidth_GBps':float(directional_gbps),'bidirectional_bandwidth_GBps':float(bidirectional_gbps),'peak_ring_seconds':float(ring_time),'IB_40GBps_seconds':float(sent/40),'Ethernet_2_5GBps_seconds':float(sent/Fraction(5,2)),'IB_to_NVLink_ratio':float((sent/40)/ring_time),'Ethernet_to_NVLink_ratio':float((sent/Fraction(5,2))/ring_time),'one_hundred_collectives_seconds':float(100*ring_time)},
 'cost':{'host_USD_per_hour':20,'rate_reqps':2,'USD_per_reqps_per_hour':20/2,'hypothetical_rate_reqps':250,'USD_per_reqps_per_hour_at_250':20/250},
 'scope':'Algebra under the stated point-to-point ring model and printed operands; no actual benchmark or memory-feasible training deployment demonstrated.'}
p=Path(__file__).resolve().parent/'work/independent_parent_checks.json'
p.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

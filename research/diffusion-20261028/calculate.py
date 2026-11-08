import json,pathlib
R=pathlib.Path(__file__).resolve().parent
v={'assumptions':{'status':'ILLUSTRATIVE_NOT_BENCHMARK','P_active':7_000_000_000,'prompt_tokens':1024,'output_tokens':256,'block_tokens':32,'steps_per_block':8,'full_canvas_steps':32,'bytes_per_logit':4,'vocab_size':262144,'canvas_tokens':256}}
a=v['assumptions'];P=a['P_active'];G=a['output_tokens'];B=a['block_tokens'];S=a['steps_per_block'];L=a['prompt_tokens']+G
v['block_case']={'blocks':G//B,'sequential_denoising_calls':G//B*S,'decoder_position_evaluations':G*S,'projection_flops':2*P*G*S,'projection_TFLOP':2*P*G*S/1e12,'AR_output_only_projection_TFLOP':2*P*G/1e12,'projection_work_ratio':S,'serial_depth_ratio_to_G_AR_steps':(G//B*S)/G,'exclusions':'prompt encoding, context attention, block commit encoding, output head, refresh, CFG, verification, communication; AR first-token timing also simplified'}
v['full_canvas_case']={'positions_per_forward':L,'position_evaluations':L*a['full_canvas_steps'],'projection_TFLOP':2*P*L*a['full_canvas_steps']/1e12,'exclusions':'attention and all non-projection costs; not an equal-quality comparison'}
v['canvas_float32_logits']={'bytes':a['canvas_tokens']*a['vocab_size']*a['bytes_per_logit'],'MiB':a['canvas_tokens']*a['vocab_size']*a['bytes_per_logit']/2**20,'exclusions':'sampling buffers, self-conditioning, batch multiplier, other activations'}
assert v['block_case']['decoder_position_evaluations']==2048
assert v['block_case']['projection_TFLOP']==28.672
assert v['canvas_float32_logits']['MiB']==256
(R/'calculations.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v,indent=2))

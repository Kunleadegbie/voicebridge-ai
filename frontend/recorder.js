let vbStream=null, vbContext=null, vbSource=null, vbProcessor=null, vbChunks=[], vbRecording=false;

function mergeFloat32(chunks){let n=chunks.reduce((a,c)=>a+c.length,0),out=new Float32Array(n),o=0;for(const c of chunks){out.set(c,o);o+=c.length;}return out;}
function writeStr(v,o,s){for(let i=0;i<s.length;i++)v.setUint8(o+i,s.charCodeAt(i));}
function wavBlob(samples,sampleRate){let b=new ArrayBuffer(44+samples.length*2),v=new DataView(b);writeStr(v,0,'RIFF');v.setUint32(4,36+samples.length*2,true);writeStr(v,8,'WAVE');writeStr(v,12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,sampleRate,true);v.setUint32(28,sampleRate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);writeStr(v,36,'data');v.setUint32(40,samples.length*2,true);let o=44;for(let i=0;i<samples.length;i++,o+=2){let s=Math.max(-1,Math.min(1,samples[i]));v.setInt16(o,s<0?s*0x8000:s*0x7fff,true);}return new Blob([b],{type:'audio/wav'});}

async function startVB(button){
 vbStream=await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:true,noiseSuppression:true}});
 vbContext=new (window.AudioContext||window.webkitAudioContext)(); await vbContext.resume(); vbChunks=[];
 vbSource=vbContext.createMediaStreamSource(vbStream); vbProcessor=vbContext.createScriptProcessor(4096,1,1);
 vbProcessor.onaudioprocess=e=>{if(vbRecording)vbChunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));};
 vbSource.connect(vbProcessor); vbProcessor.connect(vbContext.destination); vbRecording=true;
 button.classList.add('recording'); button.querySelector('span').textContent='Tap to stop'; document.getElementById('status').textContent='Listening…';
}
async function stopVB(button){
 vbRecording=false; vbProcessor&&vbProcessor.disconnect(); vbSource&&vbSource.disconnect(); vbStream&&vbStream.getTracks().forEach(t=>t.stop());
 let samples=mergeFloat32(vbChunks), rate=vbContext.sampleRate; await vbContext.close(); vbContext=null;
 button.classList.remove('recording'); button.querySelector('span').textContent='Tap to speak';
 sendAudio(wavBlob(samples,rate));
}
async function toggleRecording(button){try{if(vbRecording)await stopVB(button);else await startVB(button);}catch(e){document.getElementById('status').textContent='Microphone error: '+e.message;}}

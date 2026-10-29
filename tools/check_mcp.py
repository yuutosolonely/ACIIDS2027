"""Exercise a real stdio MCP handshake/list/status without paid work or network calls."""
import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def main():
    p=subprocess.Popen([sys.executable,str(ROOT/'tools/mcp/research_lab.py')],cwd=ROOT,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        text=True,encoding='utf-8')
    output=queue.Queue()
    errors=[]
    def readout():
        for line in p.stdout:
            try: output.put(json.loads(line))
            except json.JSONDecodeError: output.put({'invalid_stdout':line[:200]})
        output.put({'eof':True})
    def readerr():
        for line in p.stderr:
            errors.append(line.rstrip())
            if len(errors)>10: errors.pop(0)
    threading.Thread(target=readout,daemon=True).start()
    threading.Thread(target=readerr,daemon=True).start()
    def send(data):
        p.stdin.write(json.dumps(data)+'\n'); p.stdin.flush()
    def request(i,method,params):
        send({'jsonrpc':'2.0','id':i,'method':method,'params':params})
        while True:
            try: item=output.get(timeout=25)
            except queue.Empty: raise RuntimeError('MCP timeout: '+method)
            if item.get('eof'): raise RuntimeError('MCP exited: '+'; '.join(errors))
            if 'invalid_stdout' in item: raise RuntimeError(str(item))
            if item.get('id')==i:
                if 'error' in item: raise RuntimeError(str(item['error']))
                return item['result']
    try:
        init=request(1,'initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'aciids-setup-check','version':'0.1'}})
        send({'jsonrpc':'2.0','method':'notifications/initialized','params':{}})
        listing=request(2,'tools/list',{})
        names={t['name'] for t in listing['tools']}
        expected={'lit_search','paper_details','verify_reference','research_status'}
        if names != expected: raise RuntimeError('Unexpected tools: '+str(names))
        result=request(3,'tools/call',{'name':'research_status','arguments':{}})
        if result.get('isError'): raise RuntimeError(str(result))
        content=' '.join(c.get('text','') for c in result.get('content',[]))
        if 'CRIC-ED' not in json.dumps(result): raise RuntimeError('Wrong project status')
        print(json.dumps({'handshake':'PASS','protocol':init['protocolVersion'],'tools':sorted(names),'status_call':'PASS'},ensure_ascii=False))
    finally:
        p.terminate()
        try: p.wait(timeout=5)
        except subprocess.TimeoutExpired: p.kill(); p.wait(timeout=5)

if __name__=='__main__': main()

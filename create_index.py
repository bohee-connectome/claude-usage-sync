#!/usr/bin/env python3
"""Create index.html for GitHub Pages"""

html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Claude 100M Token Goal Tracker</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2.5em; color: #333; margin-bottom: 10px; }
        .deadline { color: #666; font-size: 1.2em; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        .stat-card .label { font-size: 0.9em; opacity: 0.9; margin-bottom: 5px; }
        .stat-card .value { font-size: 2em; font-weight: bold; }
        .progress-section { margin: 40px 0; }
        .progress-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .progress-label { font-size: 1.2em; color: #333; font-weight: bold; }
        .progress-percentage { font-size: 1.5em; font-weight: bold; color: #667eea; }
        .progress-bar-container {
            background: #e0e0e0;
            border-radius: 50px;
            height: 40px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            border-radius: 50px;
            transition: width 1s ease-out;
        }
        .progress-details {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            text-align: center;
        }
        .progress-detail {
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
        }
        .progress-detail .label { color: #666; font-size: 0.9em; margin-bottom: 5px; }
        .progress-detail .value { color: #333; font-size: 1.3em; font-weight: bold; }
        .projection {
            margin-top: 30px;
            padding: 20px;
            background: #fff3cd;
            border-radius: 10px;
            border-left: 4px solid #ffc107;
        }
        .projection.success { background: #d4edda; border-left-color: #28a745; }
        .projection.warning { background: #f8d7da; border-left-color: #dc3545; }
        .projection-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #333; }
        .loading { text-align: center; padding: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Claude 100M Token Goal</h1>
            <p class="deadline">Deadline: December 31, 2025</p>
        </div>
        <div id="loading" class="loading"><p>Loading data...</p></div>
        <div id="content" style="display: none;">
            <div class="stats-grid">
                <div class="stat-card"><div class="label">Total Devices</div><div class="value" id="totalDevices">-</div></div>
                <div class="stat-card"><div class="label">Total Sessions</div><div class="value" id="totalSessions">-</div></div>
                <div class="stat-card"><div class="label">Total Cost</div><div class="value" id="totalCost">-</div></div>
            </div>
            <div class="progress-section">
                <div class="progress-header">
                    <span class="progress-label">🎯 Goal Progress</span>
                    <span class="progress-percentage" id="percentage">0%</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progressBar" style="width: 0%"></div>
                </div>
                <div class="progress-details">
                    <div class="progress-detail"><div class="label">Target</div><div class="value">100.00M</div></div>
                    <div class="progress-detail"><div class="label">Current</div><div class="value" id="current">0M</div></div>
                    <div class="progress-detail"><div class="label">Remaining</div><div class="value" id="remaining">0M</div></div>
                </div>
            </div>
            <div id="projection" class="projection" style="display: none;">
                <div class="projection-title">🔮 Projection</div>
                <div id="projectionContent"></div>
            </div>
        </div>
    </div>
    <script>
        const GOAL=100000000;function fmt(t){return(t/1000000).toFixed(2)+"M"}async function load(){try{const devs=['yangpyungpc','bohees-macbook-air-local'];const data=(await Promise.all(devs.map(async d=>{const r=await fetch(`data/${d}.json`);return r.ok?await r.json():null}))).filter(d=>d);const u={i:0,o:0,c:0,s:0};let cost=0;data.forEach(d=>{u.i+=d.usage.input_tokens||0;u.o+=d.usage.output_tokens||0;u.c+=d.usage.cache_creation_tokens||0;u.s+=d.usage.total_sessions||0;cost+=d.estimated_cost||0});const tot=u.i+u.o+u.c,rem=GOAL-tot,pct=tot/GOAL*100;document.getElementById('totalDevices').textContent=data.length;document.getElementById('totalSessions').textContent=u.s.toLocaleString();document.getElementById('totalCost').textContent='$'+cost.toFixed(2);document.getElementById('percentage').textContent=pct.toFixed(1)+'%';document.getElementById('current').textContent=fmt(tot);document.getElementById('remaining').textContent=fmt(rem);setTimeout(()=>document.getElementById('progressBar').style.width=Math.min(pct,100)+'%',100);const now=new Date(),dl=new Date('2025-12-31T23:59:59Z'),ps=new Date('2025-10-01T00:00:00Z');const dr=Math.ceil((dl-now)/86400000);if(dr>0){const de=Math.max(1,Math.ceil((now-ps)/86400000)),avg=tot/de;const td=Math.ceil((dl-ps)/86400000),proj=avg*td,dt=rem/dr;const p=document.getElementById('projection');p.style.display='block';let h=`<p><strong>Days remaining:</strong> ${dr}</p>`;h+=`<p><strong>Daily target:</strong> ${fmt(dt)}</p>`;h+=`<p><strong>Current pace:</strong> ${fmt(avg)}/day</p>`;h+=`<p><strong>Projected total:</strong> ${fmt(proj)}</p>`;if(proj>=GOAL){p.className='projection success';h+=`<p style="margin-top:10px;font-weight:bold;">✅ ON TRACK! (+${fmt(proj-GOAL)})</p>`}else{p.className='projection warning';h+=`<p style="margin-top:10px;font-weight:bold;">⚠️ BEHIND PACE (-${fmt(GOAL-proj)})<br>Need +${fmt(dt-avg)}/day</p>`}document.getElementById('projectionContent').innerHTML=h}document.getElementById('loading').style.display='none';document.getElementById('content').style.display='block'}catch(e){document.getElementById('loading').innerHTML='<p>❌ Error loading data</p>'}}load();setInterval(load,300000);
    </script>
</body>
</html>"""

with open('C:/Users/user/claude-usage-tracker/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ Created index.html')

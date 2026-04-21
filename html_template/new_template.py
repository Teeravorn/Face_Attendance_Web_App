HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Face Recognition</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root{--bg-1:#0f172a;--bg-2:#1e293b;--glass:rgba(255,255,255,0.08);
    --border:rgba(255,255,255,0.15);--primary:#6366f1;--success:#22c55e;
    --danger:#ef4444;--warning:#f59e0b;--info:#38bdf8;
    --text-main:#f8fafc;--text-sub:#94a3b8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:Inter,system-ui,sans-serif;
    background:radial-gradient(1200px 600px at 10% 10%,#1e1b4b,transparent),
    linear-gradient(135deg,var(--bg-1),var(--bg-2));
    color:var(--text-main);min-height:100vh;}
.container{max-width:1500px;margin:auto;padding:28px;}
h1{text-align:center;font-size:2.1rem;font-weight:700;}
.subtitle{text-align:center;color:var(--text-sub);margin:6px 0 22px;}
.badge{display:inline-block;background:rgba(99,102,241,.2);border:1px solid var(--primary);
    color:#a5b4fc;padding:2px 10px;font-size:.78rem;margin-left:8px;}
.badge.active{background:rgba(34,197,94,.2);border-color:var(--success);color:#86efac;}
.tabs{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;}
.tab-btn{padding:8px 18px;border:1px solid var(--border);background:var(--glass);
    color:var(--text-sub);cursor:pointer;font-size:.88rem;transition:.2s;}
.tab-btn.active{background:var(--primary);color:white;border-color:var(--primary);}
.tab-content{display:none;}
.tab-content.active{display:block;}
.panel{background:var(--glass);padding:18px;border:1px solid var(--border);backdrop-filter:blur(16px);}
.panel h2{margin-bottom:14px;font-size:1.05rem;}

/* Live */
.live-layout{display:grid;grid-template-columns:3fr 1.4fr;gap:20px;align-items:start;}
@media(max-width:1100px){.live-layout{grid-template-columns:1fr;}}
#videoStream{width:100%;background:#000;display:block;}
.right-col{display:flex;flex-direction:column;gap:16px;}
.faces-list{max-height:260px;overflow-y:auto;}
.face-card{background:linear-gradient(180deg,rgba(255,255,255,.12),rgba(255,255,255,.05));
    padding:12px;margin-bottom:10px;border:1px solid var(--border);transition:.2s;cursor:pointer;}
.face-card:hover{transform:translateY(-2px);}
.face-card.identified{border-left:4px solid var(--success);}
.face-card.unknown{border-left:4px solid var(--danger);}
.face-card.selected{border-color:var(--primary);background:rgba(99,102,241,.15);}
.face-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;}
.face-name{font-weight:600;font-size:.92rem;}
.enroll-form-panel{background:var(--glass);padding:18px;border:1px solid var(--primary);}
.enroll-form-panel h3{margin-bottom:12px;font-size:1rem;color:#a5b4fc;}
.enroll-preview{width:80px;height:80px;border-radius:4px;object-fit:cover;
    border:2px solid var(--primary);margin-bottom:12px;display:none;}
.enroll-hint{font-size:.78rem;color:var(--text-sub);margin-bottom:10px;padding:8px;
    background:rgba(99,102,241,.1);border-left:3px solid var(--primary);}
.enroll-hint.hidden{display:none;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:18px;}
.stat-box{background:var(--glass);padding:16px;border:1px solid var(--border);text-align:center;}
.stat-value{font-size:1.6rem;font-weight:700;margin-top:4px;}
.stat-label{font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--text-sub);}

/* Session panel */
.session-bar{display:flex;align-items:center;gap:12px;padding:14px 18px;
    background:var(--glass);border:1px solid var(--border);margin-bottom:16px;flex-wrap:wrap;}
.session-bar.running{border-color:var(--success);background:rgba(34,197,94,.06);}
.session-name-input{flex:1;min-width:180px;padding:8px 12px;background:rgba(255,255,255,.08);
    border:1px solid var(--border);color:white;font-size:.9rem;}
.session-name-input:focus{outline:none;border-color:var(--primary);}
.session-info{font-size:.83rem;color:var(--text-sub);}
.session-info strong{color:#86efac;}
.pulse{display:inline-block;width:10px;height:10px;border-radius:50%;
    background:var(--success);margin-right:6px;animation:pulse 1.2s infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.3)}}

/* Countdown timer */
.timer-setup{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
.preset-btns{display:flex;gap:6px;flex-wrap:wrap;}
.preset-btn{padding:5px 10px;border:1px solid var(--border);background:rgba(255,255,255,.07);
    color:var(--text-sub);cursor:pointer;font-size:.78rem;transition:.2s;}
.preset-btn:hover,.preset-btn.active{background:rgba(99,102,241,.3);border-color:var(--primary);color:white;}
.custom-min{width:64px;padding:5px 8px;background:rgba(255,255,255,.07);
    border:1px solid var(--border);color:white;font-size:.82rem;text-align:center;}
.custom-min:focus{outline:none;border-color:var(--primary);}
.countdown-display{font-size:1.3rem;font-weight:700;font-family:monospace;
    padding:4px 14px;border:2px solid var(--success);color:#86efac;letter-spacing:.05em;}
.countdown-display.warning{border-color:var(--warning);color:var(--warning);}
.countdown-display.danger{border-color:var(--danger);color:var(--danger);animation:blink .8s infinite;}
.countdown-display.expired{border-color:var(--danger);color:var(--danger);}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.4}}

/* Alert overlay */
.timer-alert{position:fixed;inset:0;background:rgba(0,0,0,.75);backdrop-filter:blur(8px);
    display:flex;align-items:center;justify-content:center;z-index:2000;
    opacity:0;pointer-events:none;transition:opacity .3s;}
.timer-alert.show{opacity:1;pointer-events:auto;}
.timer-alert-box{background:linear-gradient(135deg,#1e293b,#0f172a);
    border:2px solid var(--warning);padding:40px;text-align:center;max-width:420px;width:90%;}
.timer-alert-icon{font-size:3rem;margin-bottom:12px;}
.timer-alert-title{font-size:1.4rem;font-weight:700;margin-bottom:8px;}
.timer-alert-sub{color:var(--text-sub);margin-bottom:24px;font-size:.9rem;}
.timer-alert-actions{display:flex;gap:10px;justify-content:center;}

/* Attendance tab */
.attendance-layout{display:grid;grid-template-columns:1.2fr 2fr;gap:20px;}
@media(max-width:1000px){.attendance-layout{grid-template-columns:1fr;}}
.attend-table{width:100%;border-collapse:collapse;font-size:.83rem;}
.attend-table th{padding:9px 12px;text-align:left;color:var(--text-sub);
    border-bottom:1px solid var(--border);font-weight:600;white-space:nowrap;}
.attend-table td{padding:9px 12px;border-bottom:1px solid rgba(255,255,255,.05);}
.attend-table tr:hover td{background:rgba(255,255,255,.03);}
.status-present{color:var(--success);font-weight:600;}
.status-absent{color:var(--danger);}
.first-seen-badge{background:rgba(56,189,248,.15);color:var(--info);
    padding:2px 8px;font-size:.74rem;border-radius:2px;}
.last-seen-badge{background:rgba(99,102,241,.15);color:#a5b4fc;
    padding:2px 8px;font-size:.74rem;border-radius:2px;}
.session-card{background:rgba(255,255,255,.06);border:1px solid var(--border);
    padding:12px 14px;margin-bottom:8px;cursor:pointer;transition:.2s;}
.session-card:hover{border-color:var(--primary);}
.session-card.selected{border-color:var(--primary);background:rgba(99,102,241,.1);}
.session-card-name{font-weight:600;font-size:.9rem;}
.session-card-meta{font-size:.76rem;color:var(--text-sub);margin-top:3px;}
.attend-summary{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px;}
.attend-sum-card{padding:12px;text-align:center;border:1px solid var(--border);background:rgba(255,255,255,.04);}
.attend-sum-card .num{font-size:1.5rem;font-weight:700;}
.attend-sum-card .lbl{font-size:.68rem;color:var(--text-sub);text-transform:uppercase;}

/* Database tab */
.db-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}
.db-person{display:flex;justify-content:space-between;align-items:center;
    padding:10px 14px;margin-bottom:7px;background:rgba(255,255,255,.06);border:1px solid var(--border);}
.db-person-name{font-weight:600;font-size:.9rem;}
.db-person-meta{font-size:.75rem;color:var(--text-sub);margin-top:2px;}
.db-person-actions{display:flex;gap:6px;flex-shrink:0;}
.db-empty{text-align:center;padding:40px;color:var(--text-sub);opacity:.7;}
.edit-name-input{padding:5px 8px;background:rgba(255,255,255,.1);
    border:1px solid var(--primary);color:white;font-size:.88rem;width:160px;}

/* Folder enroll */
.folder-layout{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
@media(max-width:900px){.folder-layout{grid-template-columns:1fr;}}
.folder-input-row{display:flex;gap:8px;margin-bottom:14px;}
.folder-input-row input{flex:1;padding:9px;background:rgba(255,255,255,.07);
    border:1px solid var(--border);color:white;font-size:.9rem;}
.folder-input-row input:focus{outline:none;border-color:var(--primary);}
.format-box{background:rgba(0,0,0,.3);padding:12px;font-size:.8rem;
    font-family:monospace;color:#86efac;line-height:1.8;margin-bottom:14px;}
.option-row{display:flex;align-items:center;gap:10px;margin-bottom:10px;
    font-size:.85rem;color:var(--text-sub);}
.option-row input[type=checkbox]{width:16px;height:16px;accent-color:var(--primary);}
.option-row input[type=number]{width:70px;padding:5px 8px;background:rgba(255,255,255,.07);
    border:1px solid var(--border);color:white;font-size:.82rem;}
.results-table{width:100%;border-collapse:collapse;font-size:.8rem;margin-top:10px;}
.results-table th{padding:7px 10px;text-align:left;color:var(--text-sub);
    border-bottom:1px solid var(--border);font-weight:600;}
.results-table td{padding:7px 10px;border-bottom:1px solid rgba(255,255,255,.05);}
.status-enrolled{color:var(--success);font-weight:600;}
.status-skipped{color:var(--warning);}
.status-failed{color:var(--danger);}
.summary-bar{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px;}
.summary-card{padding:10px;text-align:center;border:1px solid var(--border);background:rgba(255,255,255,.04);}
.summary-card .num{font-size:1.4rem;font-weight:700;}
.summary-card .lbl{font-size:.68rem;color:var(--text-sub);text-transform:uppercase;}

/* Shared */
.form-group{margin-bottom:12px;}
.form-group label{display:block;margin-bottom:4px;font-size:.82rem;color:var(--text-sub);}
.form-group input{width:100%;padding:9px;background:rgba(255,255,255,.07);
    border:1px solid var(--border);color:white;font-size:.9rem;}
.form-group input:focus{outline:none;border-color:var(--primary);}
.btn{padding:8px 16px;border:none;cursor:pointer;font-size:.85rem;transition:.2s;font-weight:500;}
.btn:hover{opacity:.85;transform:scale(1.02);}
.btn:disabled{opacity:.4;cursor:not-allowed;transform:none;}
.btn-primary{background:linear-gradient(135deg,var(--primary),#818cf8);color:white;}
.btn-success{background:var(--success);color:white;}
.btn-danger{background:var(--danger);color:white;}
.btn-secondary{background:rgba(255,255,255,.1);color:white;}
.btn-warning{background:var(--warning);color:#000;}
.btn-info{background:var(--info);color:#000;}
.btn-sm{padding:5px 11px;font-size:.78rem;}
.btn-full{width:100%;}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.3);
    border-top-color:white;border-radius:50%;animation:spin .7s linear infinite;
    margin-right:5px;vertical-align:middle;}
@keyframes spin{to{transform:rotate(360deg)}}
.confirm-box{position:fixed;inset:0;background:rgba(0,0,0,.7);display:flex;
    align-items:center;justify-content:center;z-index:1000;
    opacity:0;pointer-events:none;transition:opacity .2s;}
.confirm-box.show{opacity:1;pointer-events:auto;}
.confirm-inner{background:#1e293b;border:1px solid var(--border);
    padding:28px;max-width:380px;width:90%;text-align:center;}
.confirm-inner p{margin-bottom:20px;color:var(--text-sub);line-height:1.6;}
.confirm-inner strong{color:white;}
.confirm-actions{display:flex;gap:10px;justify-content:center;}
.toast{position:fixed;bottom:26px;right:26px;background:var(--success);color:white;
    padding:10px 20px;font-weight:600;opacity:0;transform:translateY(14px);
    transition:all .3s;z-index:9999;font-size:.88rem;max-width:340px;}
.toast.show{opacity:1;transform:translateY(0);}
.toast.error{background:var(--danger);}
.toast.warning{background:var(--warning);color:#000;}
</style>
</head>
<body>
<div class="container">
    <h1>&#128064; Face Recognition</h1>
    <p class="subtitle">QCS6490 &mdash; SCRFD + ArcFace
        <span class="badge" id="thresholdBadge">threshold: --</span>
        <span class="badge" id="dbBadge">db: --</span>
        <span class="badge active" id="sessionBadge" style="display:none">
            <span class="pulse"></span> Session running
        </span>
    </p>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('live',this)">&#127909; Live</button>
        <button class="tab-btn" onclick="switchTab('attendance',this)">&#128203; Attendance</button>
        <button class="tab-btn" onclick="switchTab('database',this)">&#128101; Database</button>
        <button class="tab-btn" onclick="switchTab('folder',this)">&#128193; Folder Enroll</button>
    </div>

    <!-- ══════════ LIVE TAB ══════════ -->
    <div id="tab-live" class="tab-content active">

        <!-- Session control bar -->
        <div class="session-bar" id="sessionBar">

            <!-- ── Before session starts ── -->
            <div id="sessionControls" style="display:flex;flex-direction:column;gap:10px;flex:1">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                    <input type="text" class="session-name-input" id="sessionNameInput"
                           placeholder="Session name (e.g. Class Jan 15 Morning)" value="">
                    <button class="btn btn-success" onclick="startSession()">&#9654; Start Session</button>
                </div>
                <!-- Timer setup row -->
                <div class="timer-setup">
                    <span style="font-size:.8rem;color:var(--text-sub);white-space:nowrap">&#9200; Duration:</span>
                    <div class="preset-btns">
                        <button class="preset-btn" onclick="setPreset(30,this)">30 min</button>
                        <button class="preset-btn" onclick="setPreset(60,this)">1 hr</button>
                        <button class="preset-btn" onclick="setPreset(90,this)">1.5 hr</button>
                        <button class="preset-btn" onclick="setPreset(120,this)">2 hr</button>
                        <button class="preset-btn" onclick="setPreset(0,this)">No limit</button>
                    </div>
                    <input type="number" class="custom-min" id="customMin"
                           placeholder="min" min="1" max="480"
                           oninput="onCustomMin()" title="Custom minutes">
                </div>
            </div>

            <!-- ── While session is running ── -->
            <div id="sessionRunning" style="display:none;align-items:center;gap:14px;flex-wrap:wrap;flex:1">
                <div class="session-info" style="flex:1">
                    <span class="pulse"></span>
                    <strong id="runningName"></strong>
                    &nbsp;&bull;&nbsp; Started: <strong id="runningStart"></strong>
                    &nbsp;&bull;&nbsp; Present: <strong id="runningCount">0</strong>
                </div>
                <!-- Countdown display — shown only when duration is set -->
                <div id="countdownWrap" style="display:none;align-items:center;gap:8px">
                    <span style="font-size:.78rem;color:var(--text-sub)">Time left:</span>
                    <div class="countdown-display" id="countdownDisplay">--:--</div>
                    <button class="btn btn-secondary btn-sm" onclick="addTime(10)" title="Add 10 minutes">+10 min</button>
                </div>
                <button class="btn btn-danger btn-sm" onclick="stopSession()">&#9646;&#9646; Stop</button>
            </div>

        </div>

        <!-- Timer expired alert overlay -->
        <div class="timer-alert" id="timerAlert">
            <div class="timer-alert-box">
                <div class="timer-alert-icon">&#9200;</div>
                <div class="timer-alert-title">Session Time is Up!</div>
                <div class="timer-alert-sub" id="timerAlertSub">The session has reached its scheduled end time.</div>
                <div class="timer-alert-actions">
                    <button class="btn btn-danger" onclick="stopSessionFromAlert()">&#9646;&#9646; Stop Session</button>
                    <button class="btn btn-secondary" onclick="extendSession(15)">+15 min</button>
                    <button class="btn btn-secondary" onclick="extendSession(30)">+30 min</button>
                    <button class="btn btn-secondary" onclick="dismissAlert()">Keep Running</button>
                </div>
            </div>
        </div>

        <div class="live-layout">
            <div class="panel">
                <canvas id="videoStream" width="640" height="480" style="width:100%;background:#000;display:block;"></canvas>
                <div id="wsStatus" style="font-size:.7rem;color:var(--text-sub);margin-top:8px;text-align:center;">Connecting to stream...</div>
            </div>
            <div class="right-col">
                <div class="panel">
                    <h2>&#128270; Detected Faces <span style="font-size:.75rem;color:var(--text-sub)">(click to enroll)</span></h2>
                    <div class="faces-list" id="facesList">
                        <div style="opacity:.5;text-align:center;padding:16px">Waiting for camera...</div>
                    </div>
                </div>
                <div class="enroll-form-panel">
                    <h3>&#10010; Enroll Person</h3>
                    <div class="enroll-hint" id="enrollHint">&#8592; Click a face card above.</div>
                    <img id="enrollPreview" class="enroll-preview" src="" alt="preview">
                    <div class="form-group">
                        <label>Full Name *</label>
                        <input id="personName" placeholder="e.g. Alice Smith" disabled>
                    </div>
                    <div class="form-group">
                        <label>Person ID (optional)</label>
                        <input id="personId" placeholder="Auto-generated if empty" disabled>
                    </div>
                    <input type="hidden" id="selectedFaceIndex" value="-1">
                    <button class="btn btn-primary btn-full" id="enrollBtn" onclick="submitEnroll()" disabled>
                        &#10003; Enroll Selected Face
                    </button>
                </div>
            </div>
        </div>

        <div class="stats">
            <div class="stat-box"><div class="stat-label">In Database</div><div class="stat-value" id="dbCount">--</div></div>
            <div class="stat-box"><div class="stat-label">Detected Now</div><div class="stat-value" id="facesCount">--</div></div>
            <div class="stat-box"><div class="stat-label">Identified</div><div class="stat-value" id="identifiedCount">--</div></div>
            <div class="stat-box"><div class="stat-label">Present This Session</div><div class="stat-value" id="sessionCount">--</div></div>
        </div>
    </div>

    <!-- ══════════ ATTENDANCE TAB ══════════ -->
    <div id="tab-attendance" class="tab-content">
        <div class="attendance-layout">

            <!-- Left: session list -->
            <div>
                <div class="panel">
                    <h2>&#128203; Sessions</h2>
                    <div id="sessionList">
                        <div class="db-empty">No sessions yet.</div>
                    </div>
                </div>
            </div>

            <!-- Right: session detail -->
            <div class="panel" id="sessionDetail">
                <div class="db-empty" style="padding:60px">
                    &#8592; Select a session to view attendance
                </div>
            </div>

        </div>
    </div>

    <!-- ══════════ DATABASE TAB ══════════ -->
    <div id="tab-database" class="tab-content">
        <div class="panel">
            <div class="db-header">
                <h2 style="margin:0">&#128101; Enrolled People</h2>
                <button class="btn btn-danger btn-sm" onclick="confirmClearAll()">&#128465; Clear All</button>
            </div>
            <div id="dbList"><div class="db-empty">Loading...</div></div>
        </div>
    </div>

    <!-- ══════════ FOLDER ENROLL TAB ══════════ -->
    <div id="tab-folder" class="tab-content">
        <div class="folder-layout">
            <div>
                <div class="panel" style="margin-bottom:16px">
                    <h2>&#128193; Folder Enroll from Selfies</h2>
                    <div class="format-box">
                    Folder: Alice ← Alice_001.jpg, Alice_002.jpg | Folder: Bob ← Bob_001.jpg, Bob_002.jpg;
                    </div>
                    <div class="form-group">
                        <label>&#128193; Folder Path on Board</label>
                        <div class="folder-input-row">
                            <input type="text" id="folderPath" placeholder="/path/to/folders" value="/home/ubuntu/projects/Dataset/images">
                            <button class="btn btn-secondary" onclick="previewFolder()">Preview</button>
                        </div>
                    </div>
                    <div class="option-row">
                        <input type="checkbox" id="optOverwrite">
                        <label for="optOverwrite">Overwrite if already enrolled</label>
                    </div>
                    <div class="option-row">
                        <label>Min detection score:</label>
                        <input type="number" id="optMinScore" value="0.5" min="0.1" max="0.99" step="0.05">
                    </div>
                    <button class="btn btn-primary btn-full" id="enrollFolderBtn" onclick="startFolderEnroll()">
                        &#9654; Start Batch Enroll
                    </button>
                    <div id="folderStatus" style="margin-top:10px;font-size:.82rem;color:var(--text-sub)"></div>
                </div>
                <div class="panel">
                    <h2>&#128161; Tips</h2>
                    <ul style="font-size:.82rem;color:var(--text-sub);line-height:2;padding-left:16px">
                        <li>Clear front-facing selfie, no sunglasses</li>
                        <li>Good lighting, face centered</li>
                        <li>Min resolution 300×300px</li>
                        <li>Use overwrite to update with a better photo</li>
                    </ul>
                </div>
            </div>
            <div class="panel">
                <h2>&#128202; Results</h2>
                <div id="folderResults"><div class="db-empty">Results appear here after enrollment.</div></div>
            </div>
        </div>
    </div>
</div>

<!-- Confirm dialog -->
<div id="confirmBox" class="confirm-box">
    <div class="confirm-inner">
        <p id="confirmMsg">Are you sure?</p>
        <div class="confirm-actions">
            <button class="btn btn-secondary" onclick="closeConfirm()">Cancel</button>
            <button class="btn btn-danger" id="confirmOkBtn">Delete</button>
        </div>
    </div>
</div>
<div id="toast" class="toast"></div>

<script>
// ══ Utilities ════════════════════════════════════════
function switchTab(name, btn) {
    document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById('tab-'+name).classList.add('active');
    btn.classList.add('active');
    if(name==='attendance') loadSessions();
    if(name==='database') loadDatabase();
}

function showToast(msg, type='success') {
    const t=document.getElementById('toast');
    t.innerHTML=msg; t.className='toast show'+(type!=='success'?' '+type:'');
    setTimeout(()=>t.className='toast',3500);
}

function fmt(iso) {
    if(!iso||iso==='—') return '—';
    return new Date(iso).toLocaleTimeString();
}
function fmtDate(iso) {
    if(!iso) return '—';
    return new Date(iso).toLocaleString();
}

// ══ Session Control + Countdown Timer ════════════════
let sessionActive = false;
let timerDurationSec = 0;   // 0 = no limit
let timerRemainingSec = 0;
let timerInterval = null;
let alertShown = false;

function setPreset(minutes, btn) {
    document.querySelectorAll('.preset-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('customMin').value = '';
    timerDurationSec = minutes * 60;
}

function onCustomMin() {
    document.querySelectorAll('.preset-btn').forEach(b=>b.classList.remove('active'));
    const val = parseInt(document.getElementById('customMin').value);
    timerDurationSec = (val > 0) ? val * 60 : 0;
}

function fmtCountdown(sec) {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    if (h > 0)
        return h + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
    return String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
}

function startCountdown() {
    if (timerDurationSec <= 0) return;  // no limit set
    timerRemainingSec = timerDurationSec;
    alertShown = false;

    const display = document.getElementById('countdownDisplay');
    const wrap    = document.getElementById('countdownWrap');
    wrap.style.display = 'flex';
    display.textContent = fmtCountdown(timerRemainingSec);
    display.className = 'countdown-display';

    timerInterval = setInterval(() => {
        timerRemainingSec--;

        // Color coding
        if (timerRemainingSec <= 0) {
            clearInterval(timerInterval);
            display.textContent = '00:00';
            display.className = 'countdown-display expired';
            if (!alertShown) {
                alertShown = true;
                showTimerAlert();
            }
            return;
        } else if (timerRemainingSec <= 60) {
            display.className = 'countdown-display danger';
        } else if (timerRemainingSec <= 300) {
            display.className = 'countdown-display warning';
        }

        display.textContent = fmtCountdown(timerRemainingSec);
    }, 1000);
}

function stopCountdown() {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
    document.getElementById('countdownWrap').style.display = 'none';
    document.getElementById('countdownDisplay').textContent = '--:--';
    document.getElementById('countdownDisplay').className = 'countdown-display';
}

function addTime(minutes) {
    timerRemainingSec += minutes * 60;
    document.getElementById('countdownDisplay').className = 'countdown-display';
}

function showTimerAlert() {
    const sub = document.getElementById('timerAlertSub');
    sub.textContent = '"' + document.getElementById('runningName').textContent +
                      '" has reached its scheduled end time. What would you like to do?';
    document.getElementById('timerAlert').classList.add('show');
    // Play browser notification sound if available
    try { new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAA==').play(); } catch(e) {}
}

function dismissAlert() {
    document.getElementById('timerAlert').classList.remove('show');
}

function extendSession(minutes) {
    dismissAlert();
    timerRemainingSec = minutes * 60;
    alertShown = false;
    const display = document.getElementById('countdownDisplay');
    display.className = 'countdown-display';
    // Restart interval if it stopped
    if (!timerInterval) {
        timerInterval = setInterval(() => {
            timerRemainingSec--;
            if (timerRemainingSec <= 0) {
                clearInterval(timerInterval); timerInterval = null;
                display.textContent = '00:00';
                display.className = 'countdown-display expired';
                if (!alertShown) { alertShown = true; showTimerAlert(); }
                return;
            }
            display.className = timerRemainingSec<=60 ? 'countdown-display danger'
                              : timerRemainingSec<=300 ? 'countdown-display warning'
                              : 'countdown-display';
            display.textContent = fmtCountdown(timerRemainingSec);
        }, 1000);
    }
    showToast('+' + minutes + ' min added');
}

function stopSessionFromAlert() {
    dismissAlert();
    stopSession();
}

function startSession() {
    const name = document.getElementById('sessionNameInput').value.trim() ||
                 'Session ' + new Date().toLocaleString();
    document.getElementById('sessionNameInput').value = name;

    fetch('/session_start', {method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({session_name: name})
    }).then(r=>r.json()).then(data=>{
        if(data.success) {
            sessionActive = true;
            document.getElementById('sessionControls').style.display='none';
            document.getElementById('sessionRunning').style.display='flex';
            document.getElementById('runningName').textContent = name;
            document.getElementById('runningStart').textContent = new Date().toLocaleTimeString();
            document.getElementById('sessionBar').classList.add('running');
            document.getElementById('sessionBadge').style.display='inline-block';

            // Start countdown if duration was set
            startCountdown();

            const durText = timerDurationSec > 0
                ? ' (' + fmtCountdown(timerDurationSec) + ')'
                : ' (no time limit)';
            showToast('&#9654; Session started: ' + name + durText);
        }
    });
}

function stopSession() {
    stopCountdown();
    fetch('/session_stop', {method:'POST'}).then(r=>r.json()).then(data=>{
        if(data.success) {
            sessionActive = false;
            document.getElementById('sessionControls').style.display='flex';
            document.getElementById('sessionRunning').style.display='none';
            document.getElementById('sessionBar').classList.remove('running');
            document.getElementById('sessionBadge').style.display='none';
            document.getElementById('sessionNameInput').value='';
            // Reset preset buttons
            document.querySelectorAll('.preset-btn').forEach(b=>b.classList.remove('active'));
            document.getElementById('customMin').value='';
            timerDurationSec = 0;
            showToast('Session ended — ' + data.summary.present_count + ' people present');
        }
    });
}

// ══ WebSocket Connection ══════════════════════════════
let ws = null;
let wsReconnectTimeout = null;
let wsReconnectDelay = 1000;

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('[WS] Connected');
        document.getElementById('wsStatus').textContent = '✓ Streaming';
        document.getElementById('wsStatus').style.color = '#86efac';
        wsReconnectDelay = 1000; // Reset backoff on successful connection
    };
    
    ws.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            
            if (message.type === 'frame') {
                // Display video frame on canvas
                const canvas = document.getElementById('videoStream');
                const ctx = canvas.getContext('2d');
                const img = new Image();
                img.onload = () => {
                    ctx.drawImage(img, 0, 0);
                };
                img.src = 'data:image/jpeg;base64,' + message.frame;
            } 
            else if (message.type === 'faces') {
                // Update face data
                updateFacesFromWS(message);
            }
        } catch(e) {
            console.error('[WS] Message parse error:', e);
        }
    };
    
    ws.onerror = (error) => {
        console.error('[WS] Error:', error);
        document.getElementById('wsStatus').textContent = '✗ Connection error';
        document.getElementById('wsStatus').style.color = '#ef4444';
    };
    
    ws.onclose = () => {
        console.log('[WS] Disconnected');
        document.getElementById('wsStatus').textContent = '⟳ Reconnecting...';
        document.getElementById('wsStatus').style.color = '#f59e0b';
        // Attempt reconnection with exponential backoff
        wsReconnectTimeout = setTimeout(() => {
            wsReconnectDelay = Math.min(wsReconnectDelay * 1.5, 30000);
            initWebSocket();
        }, wsReconnectDelay);
    };
}

function updateFacesFromWS(data) {
    document.getElementById('facesCount').textContent = data.faces.length;
    document.getElementById('dbCount').textContent = data.db_size;
    document.getElementById('identifiedCount').textContent = data.faces.filter(f=>f.identified).length;
    document.getElementById('sessionCount').textContent = data.session_present;
    document.getElementById('thresholdBadge').textContent = 'threshold: ' + data.threshold;
    document.getElementById('dbBadge').textContent = 'db: ' + data.db_size + ' people';
    if(data.session_active) {
        document.getElementById('runningCount').textContent = data.session_present;
    }

    const list = document.getElementById('facesList');
    if(!data.faces.length) {
        list.innerHTML = '<div style="opacity:.5;text-align:center;padding:16px">No faces detected</div>';
        clearEnrollForm();
        return;
    }
    
    list.innerHTML = data.faces.map((face,i) => `
        <div class="face-card ${face.identified?'identified':'unknown'} ${selectedFaceIndex===i?'selected':''}"
             onclick="selectFace(${i})" id="faceCard${i}">
            <div class="face-header">
                <div class="face-name">${face.identified?'&#10003; '+face.matches[0].name:'&#10067; Unknown'}</div>
                <span style="font-size:.73rem;color:var(--text-sub)">Face ${i+1}</span>
            </div>
            ${face.identified?`<div style="font-size:.77rem;color:#86efac">
                Match: ${(face.matches[0].similarity*100).toFixed(1)}%
                ${face.first_seen_this_session?'<span style="color:var(--info);margin-left:6px">&#128336; First seen</span>':''}
            </div>`:''}
            <div style="font-size:.74rem;color:var(--text-sub);margin-top:3px">
                Detection: ${face.detection_score.toFixed(3)}
                ${face.last_seen?'&nbsp;&bull;&nbsp;Last: '+face.last_seen:''}
            </div>
        </div>
    `).join('');
    
    if(selectedFaceIndex >= data.faces.length) clearEnrollForm();
}

// ══ Live Detection ════════════════════════════════════
let selectedFaceIndex = -1;

function updateFaces() {
    fetch('/get_faces').then(r=>r.json()).then(data=>{
        document.getElementById('facesCount').textContent=data.faces.length;
        document.getElementById('dbCount').textContent=data.db_size;
        document.getElementById('identifiedCount').textContent=data.faces.filter(f=>f.identified).length;
        document.getElementById('sessionCount').textContent=data.session_present;
        document.getElementById('thresholdBadge').textContent='threshold: '+data.threshold;
        document.getElementById('dbBadge').textContent='db: '+data.db_size+' people';
        if(data.session_active) {
            document.getElementById('runningCount').textContent=data.session_present;
        }

        const list=document.getElementById('facesList');
        if(!data.faces.length) {
            list.innerHTML='<div style="opacity:.5;text-align:center;padding:16px">No faces detected</div>';
            clearEnrollForm(); return;
        }
        list.innerHTML=data.faces.map((face,i)=>`
            <div class="face-card ${face.identified?'identified':'unknown'} ${selectedFaceIndex===i?'selected':''}"
                 onclick="selectFace(${i})" id="faceCard${i}">
                <div class="face-header">
                    <div class="face-name">${face.identified?'&#10003; '+face.matches[0].name:'&#10067; Unknown'}</div>
                    <span style="font-size:.73rem;color:var(--text-sub)">Face ${i+1}</span>
                </div>
                ${face.identified?`<div style="font-size:.77rem;color:#86efac">
                    Match: ${(face.matches[0].similarity*100).toFixed(1)}%
                    ${face.first_seen_this_session?'<span style="color:var(--info);margin-left:6px">&#128336; First seen</span>':''}
                </div>`:''}
                <div style="font-size:.74rem;color:var(--text-sub);margin-top:3px">
                    Detection: ${face.detection_score.toFixed(3)}
                    ${face.last_seen?'&nbsp;&bull;&nbsp;Last: '+face.last_seen:''}
                </div>
            </div>
        `).join('');
        if(selectedFaceIndex>=data.faces.length) clearEnrollForm();
    }).catch(()=>{});
}

function selectFace(index) {
    selectedFaceIndex=index;
    document.getElementById('selectedFaceIndex').value=index;
    document.querySelectorAll('.face-card').forEach((c,i)=>c.classList.toggle('selected',i===index));
    document.getElementById('enrollHint').classList.add('hidden');
    document.getElementById('personName').disabled=false;
    document.getElementById('personId').disabled=false;
    document.getElementById('enrollBtn').disabled=false;
    document.getElementById('personName').focus();
    fetch('/get_face_crop?index='+index).then(r=>r.json()).then(data=>{
        if(data.crop_b64){
            const p=document.getElementById('enrollPreview');
            p.src='data:image/jpeg;base64,'+data.crop_b64; p.style.display='block';
        }
    }).catch(()=>{});
}

function clearEnrollForm() {
    selectedFaceIndex=-1;
    document.getElementById('selectedFaceIndex').value=-1;
    document.getElementById('enrollHint').classList.remove('hidden');
    document.getElementById('enrollPreview').style.display='none';
    document.getElementById('personName').value='';
    document.getElementById('personName').disabled=true;
    document.getElementById('personId').value='';
    document.getElementById('personId').disabled=true;
    document.getElementById('enrollBtn').disabled=true;
}

function submitEnroll() {
    const name=document.getElementById('personName').value.trim();
    const pidVal=document.getElementById('personId').value.trim();
    const faceIndex=parseInt(document.getElementById('selectedFaceIndex').value);
    if(!name){showToast('Please enter a name','error');return;}
    if(faceIndex<0){showToast('Please select a face first','error');return;}
    const person_id=pidVal||'person_'+Math.random().toString(36).slice(2,9);
    fetch('/enroll',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({face_index:faceIndex,person_id,name})
    }).then(r=>r.json()).then(data=>{
        if(data.success){
            showToast('&#10003; Enrolled '+data.name+'!');
            document.getElementById('personName').value='';
            document.getElementById('personId').value='';
        } else showToast('Failed: '+(data.error||'Unknown'),'error');
    }).catch(()=>showToast('Network error','error'));
}

// ══ Attendance Tab ════════════════════════════════════
let selectedSessionId = null;

function loadSessions() {
    fetch('/list_sessions').then(r=>r.json()).then(data=>{
        const list = document.getElementById('sessionList');
        if(!data.sessions.length) {
            list.innerHTML='<div class="db-empty">No sessions recorded yet.<br>Start a session in the Live tab.</div>';
            return;
        }
        list.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <span style="font-size:.8rem;color:var(--text-sub)">${data.sessions.length} session(s)</span>
                <button class="btn btn-danger btn-sm" onclick="confirmDeleteAllSessions()">&#128465; Delete All</button>
            </div>
        ` + data.sessions.map(s=>`
            <div class="session-card ${selectedSessionId===s.session_id?'selected':''}"
                 style="display:flex;justify-content:space-between;align-items:center;gap:8px">
                <div style="flex:1;min-width:0" onclick="loadSessionDetail('${s.session_id}')" style="cursor:pointer">
                    <div class="session-card-name">&#128203; ${s.session_name}</div>
                    <div class="session-card-meta">
                        ${fmtDate(s.started_at)} &bull;
                        ${s.present_count} present &bull;
                        ${Math.round((s.duration_seconds||0)/60)} min
                    </div>
                </div>
                <button class="btn btn-danger btn-sm" style="flex-shrink:0"
                    onclick="event.stopPropagation();confirmDeleteSession('${s.session_id}','${s.session_name.replace(/'/g,"\\'").replace(/"/g,'&quot;')}')">
                    &#128465;
                </button>
            </div>
        `).join('');
    });
}

function loadSessionDetail(sessionId) {
    selectedSessionId = sessionId;
    // Re-render list to update selection highlight
    loadSessions();

    fetch('/get_session?session_id='+sessionId).then(r=>r.json()).then(data=>{
        if(!data.session) return;
        const s = data.session;
        const dbSize = data.db_size;
        const absentCount = dbSize - s.present_count;
        const duration = Math.round((s.duration_seconds||0)/60);

        const rows = Object.entries(s.records||{}).map(([pid,rec])=>`
            <tr>
                <td>${rec.name}</td>
                <td style="font-family:monospace;font-size:.78rem">${pid}</td>
                <td><span class="first-seen-badge">&#128336; ${fmt(rec.first_seen)}</span></td>
                <td><span class="last-seen-badge">&#128338; ${fmt(rec.last_seen)}</span></td>
                <td style="text-align:center">${rec.seen_count}</td>
                <td class="status-present">&#10003; Present</td>
            </tr>
        `).join('');

        // Absent people
        const absentRows = data.absent_people.map(p=>`
            <tr>
                <td>${p.name}</td>
                <td style="font-family:monospace;font-size:.78rem">${p.person_id}</td>
                <td>—</td><td>—</td><td style="text-align:center">0</td>
                <td class="status-absent">&#10005; Absent</td>
            </tr>
        `).join('');

        document.getElementById('sessionDetail').innerHTML=`
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:16px;flex-wrap:wrap;gap:10px">
                <div>
                    <h2 style="margin:0">${s.session_name}</h2>
                    <div style="font-size:.8rem;color:var(--text-sub);margin-top:4px">
                        ${fmtDate(s.started_at)} &rarr; ${s.ended_at?fmtDate(s.ended_at):'ongoing'}
                        &nbsp;&bull;&nbsp; ${duration} min
                    </div>
                </div>
                <div style="display:flex;gap:8px">
                    <button class="btn btn-info btn-sm" onclick="exportCSV('${sessionId}')">
                        &#11015; Export CSV
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDeleteSession('${sessionId}','${s.session_name.replace(/'/g,"\\'").replace(/"/g,'&quot;')}')">
                        &#128465; Delete Log
                    </button>
                </div>
            </div>

            <div class="attend-summary">
                <div class="attend-sum-card">
                    <div class="num">${dbSize}</div><div class="lbl">Total in DB</div></div>
                <div class="attend-sum-card" style="border-color:var(--success)">
                    <div class="num" style="color:var(--success)">${s.present_count}</div><div class="lbl">Present</div></div>
                <div class="attend-sum-card" style="border-color:var(--danger)">
                    <div class="num" style="color:var(--danger)">${absentCount}</div><div class="lbl">Absent</div></div>
                <div class="attend-sum-card">
                    <div class="num">${s.present_count&&dbSize?Math.round(s.present_count/dbSize*100):0}%</div>
                    <div class="lbl">Attendance</div></div>
            </div>

            <table class="attend-table">
                <thead><tr>
                    <th>Name</th><th>Student ID</th>
                    <th>First Seen</th><th>Last Seen</th>
                    <th style="text-align:center">Times Seen</th><th>Status</th>
                </tr></thead>
                <tbody>${rows}${absentRows}</tbody>
            </table>
        `;
    });
}

function exportCSV(sessionId) {
    window.location.href = '/export_csv?session_id=' + sessionId;
}

function confirmDeleteSession(sessionId, name) {
    document.getElementById('confirmMsg').innerHTML =
        'Delete attendance log for <strong>' + name + '</strong>?<br>' +
        '<span style="font-size:.8rem;color:var(--text-sub)">This cannot be undone.</span>';
    document.getElementById('confirmOkBtn').onclick = () => {
        closeConfirm();
        deleteSession(sessionId);
    };
    document.getElementById('confirmBox').classList.add('show');
}

function confirmDeleteAllSessions() {
    document.getElementById('confirmMsg').innerHTML =
        '<strong>Delete ALL attendance logs?</strong><br>' +
        '<span style="font-size:.8rem;color:var(--text-sub)">This cannot be undone.</span>';
    document.getElementById('confirmOkBtn').onclick = () => {
        closeConfirm();
        deleteAllSessions();
    };
    document.getElementById('confirmBox').classList.add('show');
}

function deleteSession(sessionId) {
    fetch('/delete_session', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_id: sessionId})
    }).then(r=>r.json()).then(data=>{
        if(data.success) {
            showToast('Attendance log deleted');
            if(selectedSessionId === sessionId) {
                selectedSessionId = null;
                document.getElementById('sessionDetail').innerHTML =
                    '<div class="db-empty" style="padding:60px">&#8592; Select a session to view attendance</div>';
            }
            loadSessions();
        } else {
            showToast('Delete failed: ' + (data.error||''), 'error');
        }
    });
}

function deleteAllSessions() {
    fetch('/delete_all_sessions', {method:'POST'})
        .then(r=>r.json()).then(data=>{
            if(data.success) {
                showToast('All attendance logs deleted');
                selectedSessionId = null;
                document.getElementById('sessionDetail').innerHTML =
                    '<div class="db-empty" style="padding:60px">&#8592; Select a session to view attendance</div>';
                loadSessions();
            } else {
                showToast('Failed to delete logs', 'error');
            }
        });
}

// ══ Database Tab ══════════════════════════════════════
function loadDatabase() {
    fetch('/list_people').then(r=>r.json()).then(data=>{
        const list=document.getElementById('dbList');
        if(!data.people.length){
            list.innerHTML='<div class="db-empty">No people enrolled yet.</div>'; return;
        }
        list.innerHTML=data.people.map(p=>`
            <div class="db-person">
                <div style="flex:1">
                    <div class="db-person-name" id="name-display-${p.person_id}">&#128100; ${p.name}</div>
                    <div class="db-person-meta">ID: ${p.person_id} &bull; ${fmtDate(p.enrolled_at)}</div>
                </div>
                <div class="db-person-actions">
                    <button class="btn btn-warning btn-sm"
                        onclick="startEditName('${p.person_id}','${p.name.replace(/'/g,"\\'")}')">&#9998;</button>
                    <button class="btn btn-danger btn-sm"
                        onclick="confirmDelete('${p.person_id}','${p.name.replace(/'/g,"\\'")}')">&#128465;</button>
                </div>
            </div>
        `).join('');
    });
}

function startEditName(personId, currentName) {
    document.getElementById('name-display-'+personId).innerHTML=`
        <input class="edit-name-input" id="edit-${personId}" value="${currentName}"
               onkeydown="handleEditKey(event,'${personId}')">
        <button class="btn btn-success btn-sm" style="margin-left:6px" onclick="saveEditName('${personId}')">Save</button>
        <button class="btn btn-secondary btn-sm" style="margin-left:4px" onclick="loadDatabase()">Cancel</button>
    `;
    document.getElementById('edit-'+personId).focus();
}
function handleEditKey(e,pid){if(e.key==='Enter')saveEditName(pid);if(e.key==='Escape')loadDatabase();}
function saveEditName(personId){
    const n=document.getElementById('edit-'+personId).value.trim();
    if(!n){showToast('Name cannot be empty','error');return;}
    fetch('/rename_person',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({person_id:personId,name:n})
    }).then(r=>r.json()).then(data=>{
        if(data.success){showToast('Renamed to '+n);loadDatabase();}
        else showToast('Rename failed','error');
    });
}
function confirmDelete(pid,name){
    document.getElementById('confirmMsg').innerHTML=`Delete <strong>${name}</strong>?`;
    document.getElementById('confirmOkBtn').onclick=()=>{closeConfirm();deletePerson(pid,name);};
    document.getElementById('confirmBox').classList.add('show');
}
function confirmClearAll(){
    document.getElementById('confirmMsg').innerHTML='<strong>Delete ALL enrolled people?</strong><br>Cannot be undone.';
    document.getElementById('confirmOkBtn').onclick=()=>{closeConfirm();clearAll();};
    document.getElementById('confirmBox').classList.add('show');
}
function closeConfirm(){document.getElementById('confirmBox').classList.remove('show');}
function deletePerson(pid,name){
    fetch('/delete_person',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({person_id:pid})
    }).then(r=>r.json()).then(data=>{
        if(data.success){showToast('Deleted '+name);loadDatabase();}
        else showToast('Delete failed','error');
    });
}
function clearAll(){
    fetch('/clear_database',{method:'POST'}).then(r=>r.json()).then(data=>{
        if(data.success){showToast('Database cleared');loadDatabase();}
        else showToast('Failed','error');
    });
}

// ══ Folder Enroll Tab ════════════════════════════════
function previewFolder(){
    const folder=document.getElementById('folderPath').value.trim();
    if(!folder){showToast('Enter a folder path','error');return;}
    document.getElementById('folderStatus').textContent='Checking...';
    fetch('/preview_folder',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({folder})
    }).then(r=>r.json()).then(data=>{
        document.getElementById('folderStatus').textContent=data.success
            ?'✓ Found '+data.count+' image(s): '+data.files.slice(0,4).join(', ')+(data.count>4?'...':'')
            :'✗ '+data.error;
    });
}
function startFolderEnroll(){
    const folder=document.getElementById('folderPath').value.trim();
    if(!folder){showToast('Enter a folder path','error');return;}
    const overwrite=document.getElementById('optOverwrite').checked;
    const minScore=parseFloat(document.getElementById('optMinScore').value)||0.5;
    const btn=document.getElementById('enrollFolderBtn');
    btn.disabled=true; btn.innerHTML='<span class="spinner"></span> Enrolling...';
    document.getElementById('folderStatus').textContent='Processing...';
    document.getElementById('folderResults').innerHTML='<div class="db-empty">Processing...</div>';
    fetch('/folder_enroll',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({folder,overwrite,min_score:minScore})
    }).then(r=>r.json()).then(data=>{
        btn.disabled=false; btn.innerHTML='&#9654; Start Batch Enroll';
        if(!data.success){
            document.getElementById('folderStatus').textContent='✗ '+data.error;
            showToast(data.error,'error'); return;
        }
        document.getElementById('folderStatus').textContent=
            `✓ Done — ${data.enrolled} enrolled, ${data.skipped} skipped, ${data.failed} failed`;
        document.getElementById('folderResults').innerHTML=`
            <div class="summary-bar">
                <div class="summary-card"><div class="num">${data.total}</div><div class="lbl">Total</div></div>
                <div class="summary-card" style="border-color:var(--success)">
                    <div class="num" style="color:var(--success)">${data.enrolled}</div><div class="lbl">Enrolled</div></div>
                <div class="summary-card" style="border-color:var(--warning)">
                    <div class="num" style="color:var(--warning)">${data.skipped}</div><div class="lbl">Skipped</div></div>
                <div class="summary-card" style="border-color:var(--danger)">
                    <div class="num" style="color:var(--danger)">${data.failed}</div><div class="lbl">Failed</div></div>
            </div>
            <table class="results-table">
                <thead><tr><th>File</th><th>Name</th><th>ID</th><th>Score</th><th>Status</th></tr></thead>
                <tbody>${data.results.map(r=>`
                    <tr>
                        <td style="color:var(--text-sub);font-size:.76rem">${r.file}</td>
                        <td>${r.name}</td>
                        <td style="font-family:monospace;font-size:.76rem">${r.person_id}</td>
                        <td>${r.detection_score!==undefined?r.detection_score:'—'}</td>
                        <td class="status-${r.status}">
                            ${{enrolled:'&#10003;',skipped:'&#8594;',failed:'&#10005;'}[r.status]}
                            ${r.status}${r.reason?' ('+r.reason+')':''}
                        </td>
                    </tr>`).join('')}
                </tbody>
            </table>`;
        if(data.enrolled>0) showToast('&#10003; Enrolled '+data.enrolled+' people!');
    }).catch(err=>{
        btn.disabled=false; btn.innerHTML='&#9654; Start Batch Enroll';
        showToast('Error: '+err,'error');
    });
}

// ══ Keyboard ══════════════════════════════════════════
document.addEventListener('keydown',e=>{
    if(e.key==='Escape') closeConfirm();
    if(e.key==='Enter'&&selectedFaceIndex>=0&&!document.getElementById('enrollBtn').disabled) submitEnroll();
});
document.getElementById('confirmBox').addEventListener('click',e=>{
    if(e.target===document.getElementById('confirmBox')) closeConfirm();
});

// Initialize WebSocket connection on page load
initWebSocket();
</script>
</body>
</html>
"""
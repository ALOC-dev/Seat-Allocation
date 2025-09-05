// 전역 상태
let currentMembers = [];
let currentGroups = {};
let currentTeams = [];
let isLoading = false;
let allocationCount = parseInt(localStorage.getItem('allocationCount') || '0');

// DOM 요소들
const elements = {
    shuffleBtn: document.getElementById('shuffleBtn'),
    saveImageBtn: document.getElementById('saveImageBtn'),
    settingsBtn: document.getElementById('settingsBtn'),
    classroomContainer: document.getElementById('classroomContainer'),
    totalMembers: document.getElementById('totalMembers'),
    totalTeams: document.getElementById('totalTeams'),
    groupConstraints: document.getElementById('groupConstraints'),
    conflictCount: document.getElementById('conflictCount'),
    groupsInfo: document.getElementById('groupsInfo'),
    settingsModal: document.getElementById('settingsModal'),
    closeModal: document.getElementById('closeModal'),
    membersTextarea: document.getElementById('membersTextarea'),
    memberCount: document.getElementById('memberCount'),
    membersPreview: document.getElementById('membersPreview'),
    groupsContainer: document.getElementById('groupsContainer'),
    addGroupBtn: document.getElementById('addGroupBtn'),
    groupCount: document.getElementById('groupCount'),
    groupsPreview: document.getElementById('groupsPreview'),
    saveSettingsBtn: document.getElementById('saveSettingsBtn'),
    cancelSettingsBtn: document.getElementById('cancelSettingsBtn'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    toast: document.getElementById('toast'),
    logContainer: document.getElementById('logContainer')
};

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadSampleData();
});

function initializeApp() {
    console.log('🚀 Smart Seat Allocation 초기화 중...');
    loadAllocationLogs();
    loadLastTeams();
    updateUI();
}

function setupEventListeners() {
    // 버튼 이벤트
    elements.shuffleBtn.addEventListener('click', shuffleSeats);
    elements.saveImageBtn.addEventListener('click', saveAsImage);
    elements.settingsBtn.addEventListener('click', openSettings);
    elements.closeModal.addEventListener('click', closeSettings);
    elements.saveSettingsBtn.addEventListener('click', saveSettings);
    elements.cancelSettingsBtn.addEventListener('click', closeSettings);
    elements.addGroupBtn.addEventListener('click', addGroupInput);
    
    // 멤버 입력 실시간 파싱
    elements.membersTextarea.addEventListener('input', updateMembersPreview);
    
    // 모달 백드롭 클릭
    elements.settingsModal.addEventListener('click', (e) => {
        if (e.target === elements.settingsModal || e.target.classList.contains('modal-backdrop')) {
            closeSettings();
        }
    });
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.settingsModal.classList.contains('active')) {
            closeSettings();
        }
    });
}

async function loadSampleData() {
    try {
        // 서버에서 데이터 로드 시도
        await loadDataFromServer();
        console.log('✅ 서버에서 데이터를 로드했습니다.');
        
        // 서버가 새로 시작되었는지 확인하고 기록 초기화
        await checkServerRestartAndClearLogs();
    } catch (error) {
        console.log('⚠️ 서버 데이터 로드 실패, 기본 데이터를 사용합니다.');
        // 기본 데이터
        currentMembers = [
            '김세현', '박종혁', '배주연', '손수빈', '황지인', '22동현',
            '김정훈', '배인수', '송희영', '이도권', '이준형', '이채우',
            '최문기', '허준재', '21동현', '김동환', '나윤서', '박도현',
            '박주영', '유영호', '이태권', '조우형', '최정혁'
        ];
        
        currentGroups = {
            '친한친구': ['김세현', '박종혁', '배주연'],
            '게임팀': ['손수빈', '황지인', '22동현'],
            '스터디그룹': ['김정훈', '배인수', '송희영', '이도권'],
            '운동팀': ['이준형', '이채우', '최문기']
        };
    }
    
    updateUI();
}

// 서버에서 데이터 로드
async function loadDataFromServer() {
    const [membersResponse, groupsResponse] = await Promise.all([
        fetch('/api/members'),
        fetch('/api/groups')
    ]);
    
    if (!membersResponse.ok || !groupsResponse.ok) {
        throw new Error('API 호출 실패');
    }
    
    const membersData = await membersResponse.json();
    const groupsData = await groupsResponse.json();
    
    if (membersData.success && groupsData.success) {
        currentMembers = membersData.members;
        currentGroups = groupsData.groups;
    } else {
        throw new Error('데이터 로드 실패');
    }
}

// 모둠 크기 계산 (Python 로직 포팅)
function calculateGroupSizes(totalMembers, maxPerGroup = 6) {
    if (totalMembers <= 0) return [];
    if (totalMembers <= maxPerGroup) return [totalMembers];
    
    let numGroups = 1;
    while (totalMembers / numGroups > maxPerGroup) {
        numGroups++;
    }
    
    const avgPerGroup = totalMembers / numGroups;
    
    if (Number.isInteger(avgPerGroup)) {
        return new Array(numGroups).fill(avgPerGroup);
    }
    
    const floorSize = Math.floor(avgPerGroup);
    const ceilSize = floorSize + 1;
    const numCeilGroups = totalMembers - (floorSize * numGroups);
    const numFloorGroups = numGroups - numCeilGroups;
    
    return [
        ...new Array(numCeilGroups).fill(ceilSize),
        ...new Array(numFloorGroups).fill(floorSize)
    ];
}

// 멤버가 속한 그룹들 찾기
function findMemberGroups(member, groups) {
    const memberGroups = [];
    for (const [groupName, groupMembers] of Object.entries(groups)) {
        if (groupMembers.includes(member)) {
            memberGroups.push(groupName);
        }
    }
    return memberGroups;
}

// 같은 그룹 멤버 수 계산
function countSameGroupMembers(member, team, groups) {
    if (!team.length) return 0;
    
    const memberGroups = findMemberGroups(member, groups);
    if (!memberGroups.length) return 0;
    
    let count = 0;
    for (const teamMember of team) {
        const teamMemberGroups = findMemberGroups(teamMember, groups);
        if (memberGroups.some(group => teamMemberGroups.includes(group))) {
            count++;
        }
    }
    return count;
}

// 그룹 제약 조건을 고려한 자리 배치 (Python 로직 포팅)
function allocateSeatsWithGroups(members, groupSizes, groups = {}) {
    // 멤버 셔플
    const shuffledMembers = [...members];
    for (let i = shuffledMembers.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffledMembers[i], shuffledMembers[j]] = [shuffledMembers[j], shuffledMembers[i]];
    }
    
    // 팀 초기화
    const teams = groupSizes.map(() => []);
    const teamCapacities = [...groupSizes];
    let lastPlacedTeam = -1;
    
    // 각 멤버를 순서대로 배치
    for (const member of shuffledMembers) {
        let placed = false;
        
        // 다음 팀부터 시작
        let startTeamIdx = (lastPlacedTeam + 1) % teams.length;
        
        // 빈 자리가 있는 팀 찾기
        let attempts = 0;
        while (teamCapacities[startTeamIdx] === 0 && attempts < teams.length) {
            startTeamIdx = (startTeamIdx + 1) % teams.length;
            attempts++;
        }
        
        // 바퀴별로 허용 수준 증가
        const maxRounds = shuffledMembers.length;
        
        for (let roundNum = 0; roundNum < maxRounds && !placed; roundNum++) {
            const allowedSameGroup = roundNum;
            
            // 모든 팀을 순회
            for (let i = 0; i < teams.length; i++) {
                const teamIdx = (startTeamIdx + i) % teams.length;
                
                if (teamCapacities[teamIdx] === 0) continue;
                
                const sameGroupCount = countSameGroupMembers(member, teams[teamIdx], groups);
                
                if (sameGroupCount <= allowedSameGroup) {
                    teams[teamIdx].push(member);
                    teamCapacities[teamIdx]--;
                    lastPlacedTeam = teamIdx;
                    placed = true;
                    break;
                }
            }
        }
        
        // fallback: 정말 배치할 곳이 없으면 첫 번째 빈 팀에 배치
        if (!placed) {
            for (let i = 0; i < teamCapacities.length; i++) {
                if (teamCapacities[i] > 0) {
                    teams[i].push(member);
                    teamCapacities[i]--;
                    lastPlacedTeam = i;
                    break;
                }
            }
        }
    }
    
    return teams;
}

// 그룹 겹침 계산
function calculateGroupConflicts(groups, teams) {
    let conflicts = 0;
    
    for (const [groupName, groupMembers] of Object.entries(groups)) {
        const teamCounts = new Array(teams.length).fill(0);
        
        for (const member of groupMembers) {
            for (let teamIdx = 0; teamIdx < teams.length; teamIdx++) {
                if (teams[teamIdx].includes(member)) {
                    teamCounts[teamIdx]++;
                    break;
                }
            }
        }
        
        for (const count of teamCounts) {
            if (count > 1) {
                conflicts += count - 1;
            }
        }
    }
    
    return conflicts;
}

// 자리 섞기
async function shuffleSeats() {
    if (isLoading) return;
    
    showLoading(true);
    isLoading = true;
    
    try {
        // Python 백엔드 API 호출
        const response = await fetch('/api/allocate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                members: currentMembers,
                groups: currentGroups
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentTeams = data.teams;
            allocationCount++;
            localStorage.setItem('allocationCount', allocationCount);
            localStorage.setItem('lastTeams', JSON.stringify(currentTeams));
            updateUI();
            addAllocationLog(currentTeams);
            showToast('자리 배치가 완료되었습니다!', 'success');
            
            console.log('📊 배치 결과:', {
                conflicts: data.conflicts,
                stats: data.stats,
                groupDistributions: data.group_distributions
            });
        } else {
            throw new Error(data.error);
        }
        
    } catch (error) {
        console.error('자리 배치 오류:', error);
        
        // Fallback: 클라이언트 사이드 알고리즘 사용
        console.log('🔄 클라이언트 사이드 알고리즘으로 fallback...');
        try {
            const groupSizes = calculateGroupSizes(currentMembers.length);
            currentTeams = allocateSeatsWithGroups(currentMembers, groupSizes, currentGroups);
            allocationCount++;
            localStorage.setItem('allocationCount', allocationCount);
            localStorage.setItem('lastTeams', JSON.stringify(currentTeams));
            updateUI();
            addAllocationLog(currentTeams);
            showToast('오프라인 모드로 자리를 배치했습니다.', 'warning');
        } catch (fallbackError) {
            showToast('자리 배치 중 오류가 발생했습니다.', 'error');
            console.error('Fallback 오류:', fallbackError);
        }
    } finally {
        showLoading(false);
        isLoading = false;
    }
}

// UI 업데이트
function updateUI() {
    updateStats();
    updateGroupsInfo();
    updateClassroom();
}

// 통계 업데이트
function updateStats() {
    const conflicts = Object.keys(currentGroups).length > 0 
        ? calculateGroupConflicts(currentGroups, currentTeams) 
        : 0;
        
    elements.totalMembers.textContent = currentMembers.length;
    elements.totalTeams.textContent = currentTeams.length;
    elements.groupConstraints.textContent = Object.keys(currentGroups).length;
    elements.conflictCount.textContent = conflicts;
}

// 그룹 정보 업데이트
function updateGroupsInfo() {
    elements.groupsInfo.innerHTML = '';
    
    if (Object.keys(currentGroups).length === 0) {
        elements.groupsInfo.innerHTML = '<p style="color: var(--text-light); text-align: center;">설정된 그룹이 없습니다.</p>';
        return;
    }
    
    for (const [groupName, groupMembers] of Object.entries(currentGroups)) {
        const groupElement = document.createElement('div');
        groupElement.className = 'group-item';
        groupElement.innerHTML = `
            <div class="group-name">${groupName}</div>
            <div class="group-members">${groupMembers.join(', ')}</div>
        `;
        
        elements.groupsInfo.appendChild(groupElement);
    }
}

// 강의실 업데이트
function updateClassroom() {
    elements.classroomContainer.innerHTML = '';
    
    if (currentTeams.length === 0) {
        elements.classroomContainer.innerHTML = '<p style="text-align: center; color: var(--text-light); margin: 2rem;">자리를 배치해보세요!</p>';
        return;
    }
    
    // 모둠을 2개씩 행으로 나누기
    const rows = [];
    for (let i = 0; i < currentTeams.length; i += 2) {
        rows.push(currentTeams.slice(i, i + 2));
    }
    
    rows.forEach((row, rowIndex) => {
        const rowElement = document.createElement('div');
        rowElement.className = 'team-row';
        
        row.forEach((team, teamIndex) => {
            const actualTeamIndex = rowIndex * 2 + teamIndex;
            const teamElement = createTeamElement(team, actualTeamIndex + 1);
            rowElement.appendChild(teamElement);
        });
        
        elements.classroomContainer.appendChild(rowElement);
    });
}

// 모둠 요소 생성
function createTeamElement(team, teamNumber) {
    const teamDiv = document.createElement('div');
    teamDiv.className = 'team';
    teamDiv.draggable = true;
    teamDiv.dataset.teamIndex = teamNumber - 1;
    
    // 팀 헤더
    const header = document.createElement('div');
    header.className = 'team-header';
    header.innerHTML = `
        <div class="team-title">${teamNumber}모둠</div>
    `;
    
    // 팀 그리드 (3행 2열)
    const grid = document.createElement('div');
    grid.className = 'team-grid';
    
    // 6개 자리 생성 (3행 2열)
    for (let i = 0; i < 6; i++) {
        const seat = document.createElement('div');
        seat.className = 'seat';
        seat.draggable = true;
        seat.dataset.teamIndex = teamNumber - 1;
        seat.dataset.seatIndex = i;
        
        if (i < team.length) {
            // 배치된 자리
            seat.classList.add('occupied');
            seat.textContent = team[i];
            
            // 그룹 겹침 체크
            if (isConflictSeat(team[i], team, currentGroups)) {
                seat.classList.add('conflict');
                seat.title = '그룹 겹침 발생';
            }
        } else {
            // 빈 자리
            seat.classList.add('empty');
            seat.textContent = '';
        }
        
        // 드래그 이벤트 리스너 추가
        setupSeatDragEvents(seat);
        
        grid.appendChild(seat);
    }
    
    teamDiv.appendChild(header);
    teamDiv.appendChild(grid);
    
    // 팀 드래그 이벤트 리스너 추가 (DOM 추가 후)
    setupTeamDragEvents(teamDiv);
    
    return teamDiv;
}

// 충돌 자리 확인
function isConflictSeat(member, team, groups) {
    const memberGroups = findMemberGroups(member, groups);
    if (memberGroups.length === 0) return false;
    
    for (const otherMember of team) {
        if (otherMember === member) continue;
        const otherGroups = findMemberGroups(otherMember, groups);
        if (memberGroups.some(group => otherGroups.includes(group))) {
            return true;
        }
    }
    return false;
}

// 멤버 파싱 함수 (유연한 구분자 지원)
function parseMembers(text) {
    if (!text || !text.trim()) return [];
    
    // 여러 구분자로 분리: 공백, 쉼표, 줄바꿈, 탭 등
    const members = text
        .split(/[\s,\n\t]+/)
        .map(member => member.trim())
        .filter(member => member.length > 0);
    
    // 중복 제거
    return [...new Set(members)];
}

// 멤버 미리보기 업데이트
function updateMembersPreview() {
    const text = elements.membersTextarea.value;
    const members = parseMembers(text);
    
    elements.memberCount.textContent = members.length;
    
    if (members.length === 0) {
        elements.membersPreview.textContent = '입력된 내용이 없습니다';
        elements.membersPreview.className = 'preview-content empty';
    } else {
        elements.membersPreview.textContent = members.join(', ');
        elements.membersPreview.className = 'preview-content';
    }
}

// 그룹 입력 필드 추가
function addGroupInput() {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'group-input-item';
    
    const groupId = `group_${Date.now()}`;
    groupDiv.innerHTML = `
        <div class="group-input-row">
            <input type="text" 
                   class="group-name-input" 
                   placeholder="그룹명" 
                   data-group-id="${groupId}">
            <input type="text" 
                   class="group-members-input" 
                   placeholder="멤버1, 멤버2, 멤버3..." 
                   data-group-id="${groupId}">
            <button type="button" class="btn-remove-group" onclick="removeGroupInput(this)">×</button>
        </div>
    `;
    
    elements.groupsContainer.appendChild(groupDiv);
    
    // 이벤트 리스너 추가
    const nameInput = groupDiv.querySelector('.group-name-input');
    const membersInput = groupDiv.querySelector('.group-members-input');
    
    nameInput.addEventListener('input', updateGroupsPreview);
    membersInput.addEventListener('input', updateGroupsPreview);
    
    // 첫 번째 입력 필드에 포커스
    nameInput.focus();
    
    updateGroupsPreview();
}

// 그룹 입력 필드 제거
function removeGroupInput(button) {
    const groupDiv = button.closest('.group-input-item');
    groupDiv.remove();
    updateGroupsPreview();
}

// 그룹 미리보기 업데이트
function updateGroupsPreview() {
    const groups = {};
    const groupInputs = elements.groupsContainer.querySelectorAll('.group-input-item');
    
    groupInputs.forEach(groupDiv => {
        const nameInput = groupDiv.querySelector('.group-name-input');
        const membersInput = groupDiv.querySelector('.group-members-input');
        
        const groupName = nameInput.value.trim();
        const membersText = membersInput.value.trim();
        
        if (groupName && membersText) {
            const members = parseMembers(membersText);
            if (members.length > 0) {
                groups[groupName] = members;
            }
        }
    });
    
    const groupCount = Object.keys(groups).length;
    elements.groupCount.textContent = groupCount;
    
    if (groupCount === 0) {
        elements.groupsPreview.textContent = '설정된 그룹이 없습니다';
        elements.groupsPreview.className = 'preview-content empty';
    } else {
        const groupsText = Object.entries(groups)
            .map(([name, members]) => `▪ ${name}: ${members.join(', ')}`)
            .join('\n');
        elements.groupsPreview.textContent = groupsText;
        elements.groupsPreview.className = 'preview-content';
    }
}

// 현재 그룹 데이터를 UI에 로드
function loadGroupsToUI(groups) {
    // 기존 그룹 입력 필드 모두 제거
    elements.groupsContainer.innerHTML = '';
    
    // 각 그룹에 대해 입력 필드 생성
    Object.entries(groups).forEach(([groupName, members]) => {
        addGroupInput();
        const lastGroup = elements.groupsContainer.lastElementChild;
        const nameInput = lastGroup.querySelector('.group-name-input');
        const membersInput = lastGroup.querySelector('.group-members-input');
        
        nameInput.value = groupName;
        membersInput.value = members.join(', ');
    });
    
    // 그룹이 없으면 빈 입력 필드 하나 추가
    if (Object.keys(groups).length === 0) {
        addGroupInput();
    }
    
    updateGroupsPreview();
}

// UI에서 그룹 데이터 수집
function collectGroupsFromUI() {
    const groups = {};
    const groupInputs = elements.groupsContainer.querySelectorAll('.group-input-item');
    
    groupInputs.forEach(groupDiv => {
        const nameInput = groupDiv.querySelector('.group-name-input');
        const membersInput = groupDiv.querySelector('.group-members-input');
        
        const groupName = nameInput.value.trim();
        const membersText = membersInput.value.trim();
        
        if (groupName && membersText) {
            const members = parseMembers(membersText);
            if (members.length > 0) {
                groups[groupName] = members;
            }
        }
    });
    
    return groups;
}

// 설정 모달
function openSettings() {
    // 현재 멤버 데이터를 텍스트에어리아에 로드
    elements.membersTextarea.value = currentMembers.join(' ');
    
    // 그룹 데이터를 새로운 UI에 로드
    loadGroupsToUI(currentGroups);
    
    // 미리보기 업데이트
    updateMembersPreview();
    updateGroupsPreview();
    
    elements.settingsModal.classList.add('active');
    elements.membersTextarea.focus();
}

function closeSettings() {
    elements.settingsModal.classList.remove('active');
}

async function saveSettings() {
    try {
        // 새로운 유연한 파싱 로직 사용
        const membersText = elements.membersTextarea.value.trim();
        const newMembers = parseMembers(membersText);
        
        // 새로운 그룹 UI에서 데이터 수집
        const newGroups = collectGroupsFromUI();
        
        if (newMembers.length === 0) {
            showToast('멤버를 최소 1명은 입력해주세요.', 'error');
            elements.membersTextarea.focus();
            return;
        }
        
        // 그룹 멤버가 전체 멤버에 포함되어 있는지 확인
        const invalidGroupMembers = [];
        Object.entries(newGroups).forEach(([groupName, groupMembers]) => {
            groupMembers.forEach(member => {
                if (!newMembers.includes(member)) {
                    invalidGroupMembers.push(`${groupName}: ${member}`);
                }
            });
        });
        
        if (invalidGroupMembers.length > 0) {
            showToast(`그룹에 포함된 멤버가 전체 멤버에 없습니다: ${invalidGroupMembers.slice(0, 3).join(', ')}${invalidGroupMembers.length > 3 ? '...' : ''}`, 'error');
            return;
        }
        
        // 서버에 저장
        await saveDataToServer(newMembers, newGroups);
        
        // 로컬 데이터 업데이트
        currentMembers = newMembers;
        currentGroups = newGroups;
        
        closeSettings();
        await shuffleSeats();
        showToast('설정이 저장되었습니다!', 'success');
        
    } catch (error) {
        console.error('설정 저장 오류:', error);
        showToast('설정 저장 중 오류가 발생했습니다.', 'error');
    }
}

// 서버에 데이터 저장
async function saveDataToServer(members, groups) {
    const [membersResponse, groupsResponse] = await Promise.all([
        fetch('/api/members', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ members })
        }),
        fetch('/api/groups', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ groups })
        })
    ]);
    
    if (!membersResponse.ok || !groupsResponse.ok) {
        throw new Error('서버 저장 실패');
    }
    
    const membersData = await membersResponse.json();
    const groupsData = await groupsResponse.json();
    
    if (!membersData.success || !groupsData.success) {
        throw new Error('서버 저장 실패');
    }
}

// 로딩 표시
function showLoading(show) {
    if (show) {
        elements.loadingOverlay.classList.add('active');
        elements.shuffleBtn.disabled = true;
    } else {
        elements.loadingOverlay.classList.remove('active');
        elements.shuffleBtn.disabled = false;
    }
}

// 토스트 알림
function showToast(message, type = 'success') {
    const toast = elements.toast;
    const icon = toast.querySelector('.toast-icon');
    const messageEl = toast.querySelector('.toast-message');
    
    // 아이콘 설정
    if (type === 'success') {
        icon.textContent = '✅';
    } else if (type === 'error') {
        icon.textContent = '❌';
    } else if (type === 'warning') {
        icon.textContent = '⚠️';
    }
    
    messageEl.textContent = message;
    
    // 토스트 표시
    toast.classList.add('active');
    
    // 3초 후 자동 숨김
    setTimeout(() => {
        toast.classList.remove('active');
    }, 3000);
}

// 서버 재시작 확인 및 로그 초기화
async function checkServerRestartAndClearLogs() {
    try {
        const response = await fetch('/api/health');
        if (response.ok) {
            const serverStartTime = response.headers.get('X-Server-Start-Time') || Date.now().toString();
            const lastServerStartTime = localStorage.getItem('lastServerStartTime');
            
            // 서버가 재시작되었다면 로그 초기화
            if (lastServerStartTime !== serverStartTime) {
                console.log('🔄 서버 재시작 감지, 배치 기록을 초기화합니다.');
                localStorage.removeItem('allocationLogs');
                localStorage.removeItem('lastTeams');
                localStorage.setItem('allocationCount', '0');
                allocationCount = 0;
                currentTeams = [];
                
                // 로그 컨테이너 초기화
                const logContainer = elements.logContainer;
                logContainer.innerHTML = '<p class="log-empty">아직 배치 기록이 없습니다.</p>';
                
                localStorage.setItem('lastServerStartTime', serverStartTime);
            }
        }
    } catch (error) {
        console.log('서버 상태 확인 실패, 기록 초기화를 건너뜁니다.');
    }
}

// localStorage에서 마지막 팀 배치 불러오기
function loadLastTeams() {
    const lastTeams = localStorage.getItem('lastTeams');
    if (lastTeams) {
        try {
            currentTeams = JSON.parse(lastTeams);
        } catch (error) {
            console.error('마지막 팀 데이터 로드 실패:', error);
            currentTeams = [];
        }
    }
}

// localStorage에서 배치 로그 불러오기
function loadAllocationLogs() {
    const logs = JSON.parse(localStorage.getItem('allocationLogs') || '[]');
    const logContainer = elements.logContainer;
    
    // 빈 메시지 제거
    const emptyMessage = logContainer.querySelector('.log-empty');
    if (emptyMessage) {
        emptyMessage.remove();
    }
    
    // 저장된 로그들을 역순으로 표시 (최신이 위로)
    logs.reverse().forEach(log => {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <span class="log-number">#${log.number}</span>
            <span class="log-time">${log.time}</span>
            <span class="log-teams">${log.teams}</span>
        `;
        logContainer.appendChild(logEntry);
    });
}

// localStorage에 배치 로그 저장
function saveAllocationLogs(logData) {
    let logs = JSON.parse(localStorage.getItem('allocationLogs') || '[]');
    
    // 새 로그 추가
    logs.push(logData);
    
    // 최대 10개만 유지
    if (logs.length > 10) {
        logs = logs.slice(-10);
    }
    
    localStorage.setItem('allocationLogs', JSON.stringify(logs));
}

// 배치 로그 추가
function addAllocationLog(teams) {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    // 팀 정보를 문자열로 변환
    const teamsString = teams.map((team, index) => {
        const teamMembers = team.join(', ');
        return `${index + 1}모둠:[${teamMembers}]`;
    }).join(' ');
    
    // localStorage에 저장
    const logData = {
        number: allocationCount,
        time: timeString,
        teams: teamsString
    };
    saveAllocationLogs(logData);
    
    // 로그 엔트리 생성
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `
        <span class="log-number">#${allocationCount}</span>
        <span class="log-time">${timeString}</span>
        <span class="log-teams">${teamsString}</span>
    `;
    
    // 로그 컨테이너에 추가
    const logContainer = elements.logContainer;
    
    // 빈 메시지 제거
    const emptyMessage = logContainer.querySelector('.log-empty');
    if (emptyMessage) {
        emptyMessage.remove();
    }
    
    // 새 로그를 맨 위에 추가
    logContainer.insertBefore(logEntry, logContainer.firstChild);
    
    // 로그가 10개를 넘으면 오래된 것 제거
    const logEntries = logContainer.querySelectorAll('.log-entry');
    if (logEntries.length > 10) {
        logEntries[logEntries.length - 1].remove();
    }
    
    // 스크롤을 맨 위로
    logContainer.scrollTop = 0;
}

// 개별 자리 드래그 앤 드롭 설정
function setupSeatDragEvents(seat) {
    seat.addEventListener('dragstart', (e) => {
        const memberText = seat.textContent.trim();
        e.dataTransfer.setData('text/plain', JSON.stringify({
            type: 'seat',
            teamIndex: parseInt(seat.dataset.teamIndex),
            seatIndex: parseInt(seat.dataset.seatIndex),
            member: memberText || null
        }));
        seat.classList.add('dragging');
    });
    
    seat.addEventListener('dragend', (e) => {
        seat.classList.remove('dragging');
    });
    
    seat.addEventListener('dragover', (e) => {
        e.preventDefault();
        seat.classList.add('drag-over');
    });
    
    seat.addEventListener('dragleave', (e) => {
        seat.classList.remove('drag-over');
    });
    
    seat.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation(); // 이벤트 전파 중단 (부모 모둠으로 전파 방지)
        seat.classList.remove('drag-over');
        
        const dragData = JSON.parse(e.dataTransfer.getData('text/plain'));
        
        if (dragData.type === 'seat') {
            const toMemberText = seat.textContent.trim();
            swapSeats(
                dragData.teamIndex, dragData.seatIndex, dragData.member,
                parseInt(seat.dataset.teamIndex), parseInt(seat.dataset.seatIndex), toMemberText || null
            );
        }
    });
}

// 모둠 전체 드래그 앤 드롭 설정
function setupTeamDragEvents(teamDiv) {
    teamDiv.addEventListener('dragstart', (e) => {
        // 개별 자리 드래그와 구별하기 위해 자리가 아닌 경우만 처리
        if (e.target.classList.contains('seat')) {
            return; // 자리 드래그는 무시
        }
        
        e.stopPropagation();
        e.dataTransfer.setData('text/plain', JSON.stringify({
            type: 'team',
            teamIndex: parseInt(teamDiv.dataset.teamIndex)
        }));
        
        teamDiv.classList.add('dragging');
    });
    
    teamDiv.addEventListener('dragend', (e) => {
        teamDiv.classList.remove('dragging');
    });
    
    teamDiv.addEventListener('dragover', (e) => {
        e.preventDefault();
        teamDiv.classList.add('drag-over');
    });
    
    teamDiv.addEventListener('dragleave', (e) => {
        teamDiv.classList.remove('drag-over');
    });
    
    teamDiv.addEventListener('drop', (e) => {
        e.preventDefault();
        teamDiv.classList.remove('drag-over');
        
        // 만약 개별 자리(seat)에 드롭된 경우라면 여기서 처리하지 않음
        // 개별 자리의 drop 이벤트가 먼저 처리됨
        if (e.target.classList.contains('seat')) {
            return;
        }
        
        try {
            const dragData = JSON.parse(e.dataTransfer.getData('text/plain'));
            
            if (dragData.type === 'team') {
                swapTeams(dragData.teamIndex, parseInt(teamDiv.dataset.teamIndex));
            } else if (dragData.type === 'seat') {
                // 개별 자리를 모둠 전체 영역(빈 공간)에 드롭했을 때만
                const toTeamIndex = parseInt(teamDiv.dataset.teamIndex);
                moveToEmptySpotInTeam(dragData, toTeamIndex);
            }
        } catch (error) {
            console.error('드롭 데이터 파싱 실패:', error);
        }
    });
}

// 모둠의 빈 자리로 멤버 이동
function moveToEmptySpotInTeam(dragData, toTeamIndex) {
    const { teamIndex: fromTeamIndex, seatIndex: fromSeatIndex, member } = dragData;
    
    // 멤버가 없으면 아무것도 하지 않음
    if (!member) return;
    
    // 같은 팀이면 아무것도 하지 않음
    if (fromTeamIndex === toTeamIndex) return;
    
    // 목표 팀에 빈 자리가 있는지 확인
    const toTeam = currentTeams[toTeamIndex];
    if (toTeam.length >= 6) {
        showToast('해당 모둠에 빈 자리가 없습니다.', 'warning');
        return;
    }
    
    // 원본 상태 저장 (변화 감지용)
    const originalTeams = JSON.stringify(currentTeams);
    
    // 배열 깊은 복사 후 작업
    const teams = currentTeams.map(team => [...team]);
    
    // 기존 자리에서 멤버 제거
    teams[fromTeamIndex].splice(fromSeatIndex, 1);
    
    // 새 팀에 멤버 추가
    teams[toTeamIndex].push(member);
    
    // 빈 문자열 제거
    teams[fromTeamIndex] = teams[fromTeamIndex].filter(m => m && m.trim());
    teams[toTeamIndex] = teams[toTeamIndex].filter(m => m && m.trim());
    
    // 변화가 있는지 확인
    const newTeams = JSON.stringify(teams);
    if (originalTeams === newTeams) {
        return;
    }
    
    currentTeams = teams;
    
    // localStorage 업데이트
    localStorage.setItem('lastTeams', JSON.stringify(currentTeams));
    
    // UI 업데이트
    updateUI();
    
    // 이동 로그 추가
    addMoveLog(member, fromTeamIndex + 1, toTeamIndex + 1);
}

// 자리 교환
function swapSeats(fromTeam, fromSeat, fromMember, toTeam, toSeat, toMember) {
    if (fromTeam === toTeam && fromSeat === toSeat) return;
    
    // 원본 상태 저장 (변화 감지용)
    const originalTeams = JSON.stringify(currentTeams);
    
    // 배열 깊은 복사 후 작업
    const teams = currentTeams.map(team => [...team]);
    
    // 교환 로직
    if (fromMember && toMember) {
        // 둘 다 사람이면 교환
        teams[fromTeam][fromSeat] = toMember;
        teams[toTeam][toSeat] = fromMember;
    } else if (fromMember && !toMember) {
        // from의 사람을 to 팀의 빈자리로 이동
        teams[fromTeam].splice(fromSeat, 1);
        teams[toTeam].push(fromMember);
    } else if (!fromMember && toMember) {
        // to의 사람을 from 팀의 빈자리로 이동
        teams[toTeam].splice(toSeat, 1);
        teams[fromTeam].push(toMember);
    }
    
    // 빈 문자열 제거
    teams[fromTeam] = teams[fromTeam].filter(m => m && m.trim());
    teams[toTeam] = teams[toTeam].filter(m => m && m.trim());
    
    // 변화가 있는지 확인
    const newTeams = JSON.stringify(teams);
    if (originalTeams === newTeams) {
        // 변화가 없으면 로그 없이 종료
        return;
    }
    
    currentTeams = teams;
    
    // localStorage 업데이트
    localStorage.setItem('lastTeams', JSON.stringify(currentTeams));
    
    // UI 업데이트
    updateUI();
    
    // 로그 추가
    if (fromMember && toMember) {
        // 사람끼리 교환
        addSwapLog(fromMember, toMember);
    } else {
        // 사람이 빈자리로 이동
        const member = fromMember || toMember;
        const fromTeamNum = fromMember ? fromTeam + 1 : toTeam + 1;
        const toTeamNum = fromMember ? toTeam + 1 : fromTeam + 1;
        addMoveLog(member, fromTeamNum, toTeamNum);
    }
}

// 모둠 교환
function swapTeams(fromTeamIndex, toTeamIndex) {
    if (fromTeamIndex === toTeamIndex) return;
    
    // 팀 전체 교환
    const temp = currentTeams[fromTeamIndex];
    currentTeams[fromTeamIndex] = currentTeams[toTeamIndex];
    currentTeams[toTeamIndex] = temp;
    
    // localStorage 업데이트
    localStorage.setItem('lastTeams', JSON.stringify(currentTeams));
    
    // UI 업데이트
    updateUI();
    
    // 교환 로그 추가
    addTeamSwapLog(fromTeamIndex + 1, toTeamIndex + 1);
}

// 이동 로그 추가
function addMoveLog(member, fromTeam, toTeam) {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    allocationCount++;
    localStorage.setItem('allocationCount', allocationCount);
    
    const moveDescription = `${member} → ${fromTeam}모둠에서 ${toTeam}모둠으로`;
    
    // localStorage에 저장
    const logData = {
        number: allocationCount,
        time: timeString,
        teams: `이동: ${moveDescription}`
    };
    saveAllocationLogs(logData);
    
    // 로그 엔트리 생성
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry move-log';
    logEntry.innerHTML = `
        <span class="log-number">#${allocationCount}</span>
        <span class="log-time">${timeString}</span>
        <span class="log-teams">이동: ${moveDescription}</span>
    `;
    
    // 로그 컨테이너에 추가
    const logContainer = elements.logContainer;
    
    // 빈 메시지 제거
    const emptyMessage = logContainer.querySelector('.log-empty');
    if (emptyMessage) {
        emptyMessage.remove();
    }
    
    // 새 로그를 맨 위에 추가
    logContainer.insertBefore(logEntry, logContainer.firstChild);
    
    // 로그가 10개를 넘으면 오래된 것 제거
    const logEntries = logContainer.querySelectorAll('.log-entry');
    if (logEntries.length > 10) {
        logEntries[logEntries.length - 1].remove();
    }
    
    // 스크롤을 맨 위로
    logContainer.scrollTop = 0;
}

// 개별 교환 로그 추가 (사람끼리 교환할 때만)
function addSwapLog(fromMember, toMember) {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    allocationCount++;
    localStorage.setItem('allocationCount', allocationCount);
    
    const swapDescription = `${fromMember} ↔ ${toMember}`;
    
    // localStorage에 저장
    const logData = {
        number: allocationCount,
        time: timeString,
        teams: `교환: ${swapDescription}`
    };
    saveAllocationLogs(logData);
    
    // 로그 엔트리 생성
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry swap-log';
    logEntry.innerHTML = `
        <span class="log-number">#${allocationCount}</span>
        <span class="log-time">${timeString}</span>
        <span class="log-teams">교환: ${swapDescription}</span>
    `;
    
    // 로그 컨테이너에 추가
    const logContainer = elements.logContainer;
    
    // 빈 메시지 제거
    const emptyMessage = logContainer.querySelector('.log-empty');
    if (emptyMessage) {
        emptyMessage.remove();
    }
    
    // 새 로그를 맨 위에 추가
    logContainer.insertBefore(logEntry, logContainer.firstChild);
    
    // 로그가 10개를 넘으면 오래된 것 제거
    const logEntries = logContainer.querySelectorAll('.log-entry');
    if (logEntries.length > 10) {
        logEntries[logEntries.length - 1].remove();
    }
    
    // 스크롤을 맨 위로
    logContainer.scrollTop = 0;
}

// 모둠 교환 로그 추가
function addTeamSwapLog(fromTeam, toTeam) {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    allocationCount++;
    localStorage.setItem('allocationCount', allocationCount);
    
    const swapDescription = `${fromTeam}모둠 ↔ ${toTeam}모둠`;
    
    // localStorage에 저장
    const logData = {
        number: allocationCount,
        time: timeString,
        teams: `모둠교환: ${swapDescription}`
    };
    saveAllocationLogs(logData);
    
    // 로그 엔트리 생성
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry team-swap-log';
    logEntry.innerHTML = `
        <span class="log-number">#${allocationCount}</span>
        <span class="log-time">${timeString}</span>
        <span class="log-teams">모둠교환: ${swapDescription}</span>
    `;
    
    // 로그 컨테이너에 추가
    const logContainer = elements.logContainer;
    
    // 빈 메시지 제거
    const emptyMessage = logContainer.querySelector('.log-empty');
    if (emptyMessage) {
        emptyMessage.remove();
    }
    
    // 새 로그를 맨 위에 추가
    logContainer.insertBefore(logEntry, logContainer.firstChild);
    
    // 로그가 10개를 넘으면 오래된 것 제거
    const logEntries = logContainer.querySelectorAll('.log-entry');
    if (logEntries.length > 10) {
        logEntries[logEntries.length - 1].remove();
    }
    
    // 스크롤을 맨 위로
    logContainer.scrollTop = 0;
}

// PNG로 저장 기능
async function saveAsImage() {
    if (currentTeams.length === 0) {
        showToast("저장할 배치도가 없습니다. 먼저 자리를 배치해주세요.", "warning");
        return;
    }
    
    try {
        showLoading(true);
        
        // 캡처할 영역을 임시로 생성
        const captureArea = createCaptureArea();
        document.body.appendChild(captureArea);
        
        // 약간의 렌더링 지연
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // HTML2Canvas로 캡처
        const canvas = await html2canvas(captureArea, {
            backgroundColor: "#ffffff",
            scale: 2,
            useCORS: true,
            allowTaint: false,
            width: captureArea.offsetWidth,
            height: captureArea.offsetHeight
        });
        
        // 임시 영역 제거
        document.body.removeChild(captureArea);
        
        // 이미지 다운로드
        const link = document.createElement("a");
        const now = new Date();
        const timestamp = now.toISOString().slice(0, 19).replace(/[:-]/g, "").replace("T", "_");
        link.download = `자리배치_${timestamp}.png`;
        link.href = canvas.toDataURL("image/png");
        link.click();
        
        showToast("배치도가 PNG 파일로 저장되었습니다!", "success");
        
    } catch (error) {
        console.error("이미지 저장 오류:", error);
        showToast("이미지 저장 중 오류가 발생했습니다.", "error");
    } finally {
        showLoading(false);
    }
}

// 캡처용 영역 생성
function createCaptureArea() {
    const captureDiv = document.createElement("div");
    captureDiv.style.cssText = `
        position: fixed;
        top: -9999px;
        left: 0;
        background: white;
        padding: 40px;
        font-family: "Noto Sans KR", sans-serif;
        width: 1200px;
        box-sizing: border-box;
    `;
    
    // 제목 추가
    const title = document.createElement("div");
    title.style.cssText = `
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 3px solid #3b82f6;
    `;
    title.textContent = "자리 배치도";
    captureDiv.appendChild(title);
    
    // 날짜/시간 정보
    const dateInfo = document.createElement("div");
    dateInfo.style.cssText = `
        text-align: right;
        font-size: 14px;
        color: #64748b;
        margin-bottom: 30px;
    `;
    const now = new Date();
    dateInfo.textContent = `생성일시: ${now.toLocaleString("ko-KR")}`;
    captureDiv.appendChild(dateInfo);
    
    // 칠판 추가
    const blackboard = document.createElement("div");
    blackboard.style.cssText = `
        background: #2d3748;
        color: white;
        text-align: center;
        padding: 20px;
        margin-bottom: 30px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 500;
    `;
    blackboard.textContent = "🧑‍🏫 칠판";
    captureDiv.appendChild(blackboard);
    
    // 강의실 레이아웃 재생성 (웹과 동일한 형태)
    const classroomClone = document.createElement('div');
    classroomClone.style.cssText = `
        display: flex;
        flex-direction: column;
        gap: 30px;
        max-width: none;
        margin: 0;
    `;
    
    // 모둠을 2개씩 행으로 나누기 (웹과 동일한 로직)
    const rows = [];
    for (let i = 0; i < currentTeams.length; i += 2) {
        rows.push(currentTeams.slice(i, i + 2));
    }
    
    // 각 행 생성
    rows.forEach((row, rowIndex) => {
        const rowElement = document.createElement('div');
        rowElement.style.cssText = `
            display: flex;
            gap: 30px;
            justify-content: center;
        `;
        
        row.forEach((team, teamIndex) => {
            const actualTeamIndex = rowIndex * 2 + teamIndex;
            const teamElement = createTeamElementForCapture(team, actualTeamIndex + 1);
            rowElement.appendChild(teamElement);
        });
        
        classroomClone.appendChild(rowElement);
    });
    
    captureDiv.appendChild(classroomClone);
    
    // 통계 정보 추가
    const stats = document.createElement("div");
    stats.style.cssText = `
        margin-top: 30px;
        padding-top: 20px;
        border-top: 2px solid #e2e8f0;
        display: flex;
        justify-content: space-around;
        font-size: 14px;
        color: #64748b;
    `;
    
    const conflicts = calculateGroupConflicts(currentGroups, currentTeams);
    stats.innerHTML = `
        <span>총 인원: ${currentMembers.length}명</span>
        <span>모둠 수: ${currentTeams.length}개</span>
        <span>그룹 제약: ${Object.keys(currentGroups).length}개</span>
        <span>충돌 수: ${conflicts}개</span>
    `;
    
    captureDiv.appendChild(stats);
    
    return captureDiv;
}

// 캡처용 모둠 요소 생성 (드래그 없는 버전)
function createTeamElementForCapture(team, teamNumber) {
    const teamDiv = document.createElement('div');
    teamDiv.style.cssText = `
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        width: 280px;
        box-sizing: border-box;
    `;
    
    // 팀 헤더
    const header = document.createElement('div');
    header.style.cssText = `
        background: #3b82f6;
        color: white;
        text-align: center;
        padding: 12px;
        margin: -16px -16px 16px -16px;
        border-radius: 10px 10px 0 0;
        font-weight: 600;
        font-size: 16px;
    `;
    header.textContent = `${teamNumber}모둠`;
    teamDiv.appendChild(header);
    
    // 팀 그리드 (3행 2열)
    const grid = document.createElement('div');
    grid.style.cssText = `
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: repeat(3, 1fr);
        gap: 8px;
        height: 180px;
    `;
    
    // 6개 자리 생성 (3행 2열)
    for (let i = 0; i < 6; i++) {
        const seat = document.createElement('div');
        seat.style.cssText = `
            border: 1px solid #d1d5db;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: 500;
            padding: 4px;
            text-align: center;
            word-break: keep-all;
        `;
        
        if (i < team.length) {
            // 배치된 자리
            seat.style.backgroundColor = '#f8fafc';
            seat.style.borderColor = '#94a3b8';
            seat.textContent = team[i];
            
            //그룹 겹침 체크
            if (isConflictSeat(team[i], team, currentGroups)) {
                seat.style.backgroundColor = '#fee2e2';
                seat.style.borderColor = '#f87171';
                seat.style.color = '#dc2626';
            }
        } else {
            // 빈 자리
            seat.style.backgroundColor = '#f9fafb';
            seat.style.borderColor = '#e5e7eb';
            seat.style.color = '#9ca3af';
            seat.textContent = '';
        }
        
        grid.appendChild(seat);
    }
    
    teamDiv.appendChild(grid);
    
    return teamDiv;
}

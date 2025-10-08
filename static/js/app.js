// DOM 元素
const urlInput = document.getElementById('url-input');
const pasteBtn = document.getElementById('paste-btn');
const downloadBtn = document.getElementById('download-btn');
const progressSection = document.getElementById('progress-section');
const statusText = document.getElementById('status-text');
const progressDetails = document.getElementById('progress-details');
const progressBar = document.getElementById('progress-bar');
const downloadFileBtn = document.getElementById('download-file-btn');
const videoInfo = document.getElementById('video-info');
const qualitySelect = document.getElementById('quality-select');

// 音訊品質選項
const audioQualities = [
    { value: '320', text: '最佳品質 (320 kbps)' },
    { value: '256', text: '高品質 (256 kbps)' },
    { value: '192', text: '標準品質 (192 kbps)' },
    { value: '128', text: '一般品質 (128 kbps)' },
    { value: '96', text: '低品質 (96 kbps)' }
];

// 影片品質選項
const videoQualities = [
    { value: 'best', text: '最佳品質 (Best)' },
    { value: '2160p', text: '4K (2160p)' },
    { value: '1440p', text: '2K (1440p)' },
    { value: '1080p', text: 'Full HD (1080p)' },
    { value: '720p', text: 'HD (720p)' },
    { value: '480p', text: 'SD (480p)' },
    { value: '360p', text: '低品質 (360p)' }
];

let currentTaskId = null;
let progressCheckInterval = null;

// 貼上按鈕
pasteBtn.addEventListener('click', async () => {
    try {
        const text = await navigator.clipboard.readText();
        if (text) {
            urlInput.value = text;
            // 如果是 YouTube 網址，自動取得影片資訊
            if (isYouTubeUrl(text)) {
                getVideoInfo(text);
            }
        }
    } catch (err) {
        alert('無法讀取剪貼簿，請手動貼上網址');
    }
});

// 下載類型切換
document.querySelectorAll('input[name="type"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        updateQualityOptions(e.target.value);
    });
});

// 更新品質選項
function updateQualityOptions(type) {
    const qualities = type === 'audio' ? audioQualities : videoQualities;
    
    qualitySelect.innerHTML = '';
    const optgroup = document.createElement('optgroup');
    optgroup.label = type === 'audio' ? '音訊品質' : '影片品質';
    
    qualities.forEach(q => {
        const option = document.createElement('option');
        option.value = q.value;
        option.textContent = q.text;
        optgroup.appendChild(option);
    });
    
    qualitySelect.appendChild(optgroup);
}

// 檢查是否為 YouTube 網址
function isYouTubeUrl(url) {
    const patterns = [
        /^https?:\/\/(www\.)?youtube\.com\/watch\?v=/,
        /^https?:\/\/youtu\.be\//,
        /^https?:\/\/(www\.)?youtube\.com\/shorts\//
    ];
    return patterns.some(pattern => pattern.test(url));
}

// 清理 YouTube URL (移除播放清單參數)
function cleanYouTubeUrl(url) {
    try {
        const urlObj = new URL(url);
        let videoId = null;
        
        // 從 youtube.com/watch 提取
        if (urlObj.hostname.includes('youtube.com') && urlObj.pathname === '/watch') {
            videoId = urlObj.searchParams.get('v');
        }
        // 從 youtu.be 提取
        else if (urlObj.hostname === 'youtu.be') {
            videoId = urlObj.pathname.substring(1).split('?')[0];
        }
        
        if (videoId) {
            return `https://www.youtube.com/watch?v=${videoId}`;
        }
    } catch (e) {
        console.error('URL 解析錯誤:', e);
    }
    
    return url;
}

// 取得影片資訊
async function getVideoInfo(url) {
    // 先清理 URL
    const cleanedUrl = cleanYouTubeUrl(url);
    
    // 如果 URL 被清理過,更新輸入框
    if (cleanedUrl !== url) {
        urlInput.value = cleanedUrl;
        console.log('URL 已清理,移除播放清單參數');
    }
    
    try {
        const response = await fetch('/api/info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: cleanedUrl })
        });
        
        if (response.ok) {
            const data = await response.json();
            showVideoInfo(data);
        }
    } catch (err) {
        console.error('無法取得影片資訊:', err);
    }
}

// 顯示影片資訊
function showVideoInfo(data) {
    document.getElementById('video-thumbnail').src = data.thumbnail;
    document.getElementById('video-title').textContent = data.title;
    document.getElementById('video-uploader').textContent = data.uploader;
    videoInfo.style.display = 'flex';
}

// 開始下載
downloadBtn.addEventListener('click', async () => {
    let url = urlInput.value.trim();
    
    if (!url) {
        alert('請輸入 YouTube 網址');
        return;
    }
    
    if (!isYouTubeUrl(url)) {
        alert('請輸入有效的 YouTube 網址');
        return;
    }
    
    // 清理 URL (移除播放清單參數)
    url = cleanYouTubeUrl(url);
    urlInput.value = url;  // 更新顯示
    
    const type = document.querySelector('input[name="type"]:checked').value;
    const quality = qualitySelect.value;
    
    // 重置 UI
    progressSection.style.display = 'block';
    downloadFileBtn.style.display = 'none';
    downloadBtn.disabled = true;
    progressBar.style.width = '0%';
    
    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, type, quality })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentTaskId = data.task_id;
            startProgressCheck();
        } else {
            const error = await response.json();
            alert('下載失敗: ' + error.error);
            resetUI();
        }
    } catch (err) {
        alert('網路錯誤: ' + err.message);
        resetUI();
    }
});

// 開始檢查進度
function startProgressCheck() {
    if (progressCheckInterval) {
        clearInterval(progressCheckInterval);
    }
    
    progressCheckInterval = setInterval(checkProgress, 1000);
}

// 檢查下載進度
async function checkProgress() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`/api/progress/${currentTaskId}`);
        
        if (response.ok) {
            const data = await response.json();
            updateProgress(data);
            
            if (data.status === 'completed') {
                clearInterval(progressCheckInterval);
                showDownloadButton();
            } else if (data.status === 'error') {
                clearInterval(progressCheckInterval);
                alert('下載失敗: ' + data.error);
                resetUI();
            }
        }
    } catch (err) {
        console.error('檢查進度時發生錯誤:', err);
    }
}

// 更新進度顯示
function updateProgress(data) {
    const statusMap = {
        'preparing': '準備中...',
        'downloading': '下載中...',
        'processing': '處理中...',
        'completed': '完成！',
        'error': '錯誤'
    };
    
    statusText.textContent = statusMap[data.status] || data.status;
    
    if (data.status === 'downloading') {
        progressDetails.textContent = `${data.progress} | 速度: ${data.speed} | 剩餘: ${data.eta}`;
        const percent = parseFloat(data.progress) || 0;
        progressBar.style.width = percent + '%';
    } else if (data.status === 'processing') {
        progressDetails.textContent = '正在轉換格式...';
        progressBar.style.width = '100%';
    } else if (data.status === 'completed') {
        progressDetails.textContent = data.title;
        progressBar.style.width = '100%';
    }
}

// 顯示下載按鈕
function showDownloadButton() {
    downloadFileBtn.style.display = 'block';
    downloadFileBtn.onclick = () => {
        window.location.href = `/api/download/${currentTaskId}`;
        
        // 下載後重置（延遲 2 秒）
        setTimeout(resetUI, 2000);
    };
}

// 重置 UI
function resetUI() {
    downloadBtn.disabled = false;
    currentTaskId = null;
    
    setTimeout(() => {
        progressSection.style.display = 'none';
        progressBar.style.width = '0%';
        statusText.textContent = '準備中...';
        progressDetails.textContent = '';
    }, 3000);
}

// 自動檢測剪貼簿（頁面載入時）
window.addEventListener('load', async () => {
    try {
        const text = await navigator.clipboard.readText();
        if (text && isYouTubeUrl(text)) {
            urlInput.value = text;
            getVideoInfo(text);
        }
    } catch (err) {
        // 忽略錯誤（可能沒有權限）
    }
});

// URL 輸入變化時檢查
urlInput.addEventListener('blur', () => {
    const url = urlInput.value.trim();
    if (url && isYouTubeUrl(url)) {
        getVideoInfo(url);
    }
});

"""測試 URL 清理邏輯"""
from urllib.parse import urlparse, parse_qs

def clean_youtube_url(url):
    """清理 YouTube URL,移除播放清單參數"""
    # 提取影片 ID
    video_id = None
    if 'youtube.com/watch' in url:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        video_id = query_params.get('v', [None])[0]
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0]
    
    if video_id:
        # 重建乾淨的 URL (不含播放清單)
        clean_url = f'https://www.youtube.com/watch?v={video_id}'
        return clean_url
    
    return url

# 測試案例
test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDfLyHit9OnhU",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ?list=RDfLyHit9OnhU",
]

print("URL 清理測試:")
print("="*80)

for url in test_urls:
    cleaned = clean_youtube_url(url)
    print(f"\n原始 URL:")
    print(f"  {url}")
    print(f"清理後:")
    print(f"  {cleaned}")
    print(f"結果: {'✅ 成功' if 'list=' not in cleaned else '❌ 失敗'}")

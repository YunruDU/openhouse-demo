import json
import re

def build():
    with open('events.json', 'r', encoding='utf-8') as f:
        events = json.load(f)
    with open('facilities.json', 'r', encoding='utf-8') as f:
        facs = json.load(f)
    with open('registration_data.json', 'r', encoding='utf-8') as f:
        regs = json.load(f)

    print(f"Loaded {len(events)} events, {len(facs)} facilities, {len(regs)} registration records.")

    html_template = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>中研院 2026 Openhouse 院區開放活動地圖</title>
  
  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <!-- Font Awesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"/>
  <!-- Google Fonts Inter & Noto Sans TC -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">

  <style>
    :root {
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --bg-main: #f8fafc;
      --panel-bg: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border-color: #e2e8f0;
      --sidebar-width: 420px;
      --header-height: 60px;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Inter', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* 頂部導航列 */
    .app-header {
      height: var(--header-height);
      background: #ffffff;
      border-bottom: 1.5px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      z-index: 50;
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
      gap: 12px;
    }

    .header-brand {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: var(--text-main);
      flex-shrink: 0;
    }
    .brand-icon {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #2563eb, #3b82f6);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 17px;
      box-shadow: 0 3px 10px rgba(37, 99, 235, 0.3);
    }
    .brand-text h1 {
      font-size: 16px;
      font-weight: 900;
      letter-spacing: -0.3px;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }

    /* 報名戰況看板按鈕 */
    .header-reg-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 13px;
      background: linear-gradient(135deg, #eff6ff, #dbeafe);
      color: #1d4ed8;
      font-size: 12px;
      font-weight: 800;
      border-radius: 20px;
      border: 1.5px solid #bfdbfe;
      text-decoration: none;
      transition: all 0.2s ease;
      box-shadow: 0 2px 6px rgba(37, 99, 235, 0.08);
      flex-shrink: 0;
      white-space: nowrap;
    }
    .header-reg-btn:hover {
      background: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
      transform: translateY(-1px);
    }

    /* 頂部圖層控制列 */
    .header-layers-bar {
      display: flex;
      align-items: center;
      gap: 6px;
      overflow-x: auto;
      padding: 4px 0;
      scrollbar-width: none;
      flex: 1;
      justify-content: flex-start;
    }
    .header-layers-bar::-webkit-scrollbar { display: none; }

    .layer-chip {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 9px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      border: 1.5px solid #cbd5e1;
      background: #f8fafc;
      color: #475569;
      user-select: none;
      transition: all 0.15s ease;
      white-space: nowrap;
    }
    .layer-chip:hover {
      border-color: #94a3b8;
      background: #f1f5f9;
    }
    .layer-chip.active {
      background: #0f172a;
      color: #ffffff;
      border-color: #0f172a;
      box-shadow: 0 2px 6px rgba(15, 23, 42, 0.2);
    }

    .layer-chip[data-layer="events"].active { background: #2563eb; border-color: #2563eb; }
    .layer-chip[data-layer="接待與服務"].active { background: #ea580c; border-color: #ea580c; }
    .layer-chip[data-layer="餐飲資訊"].active { background: #dc2626; border-color: #dc2626; }
    .layer-chip[data-layer="休憩場所"].active { background: #16a34a; border-color: #16a34a; }
    .layer-chip[data-layer="哺集乳室"].active { background: #9333ea; border-color: #9333ea; }
    .layer-chip[data-layer="洗手間"].active { background: #0284c7; border-color: #0284c7; }
    .layer-chip[data-layer="箱水及飲水機"].active { background: #0891b2; border-color: #0891b2; }
    .layer-chip[data-layer="免費接駁車"].active { background: #d97706; border-color: #d97706; }
    .layer-chip[data-layer="停車與交通資訊"].active { background: #475569; border-color: #475569; }

    /* 主畫面佈局 (側邊欄 + 地圖) */
    .app-main {
      flex: 1;
      display: flex;
      position: relative;
      overflow: hidden;
    }

    /* 左側側邊欄 */
    .sidebar-panel {
      width: var(--sidebar-width);
      background: var(--panel-bg);
      border-right: 1.5px solid var(--border-color);
      display: flex;
      flex-direction: column;
      height: 100%;
      z-index: 20;
      box-shadow: 4px 0 16px rgba(0,0,0,0.03);
    }

    .sidebar-filters {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border-color);
      background: #ffffff;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    /* 搜尋列 */
    .search-box {
      position: relative;
      width: 100%;
    }
    .search-box i {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: #94a3b8;
      font-size: 13px;
    }
    .search-input {
      width: 100%;
      padding: 8px 12px 8px 34px;
      border-radius: 8px;
      border: 1.5px solid #cbd5e1;
      font-size: 13px;
      background: #f8fafc;
      color: var(--text-main);
      outline: none;
      transition: all 0.2s;
    }
    .search-input:focus {
      border-color: var(--primary);
      background: #ffffff;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }

    /* 主題切換大按鈕卡片列 */
    .theme-card-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    .theme-card-chip {
      padding: 7px 6px;
      border-radius: 8px;
      font-size: 11.5px;
      font-weight: 800;
      cursor: pointer;
      background: #f1f5f9;
      color: #475569;
      border: 1.5px solid #cbd5e1;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      white-space: nowrap;
    }
    .theme-card-chip:hover {
      background: #e2e8f0;
      color: #0f172a;
    }
    .theme-card-chip.active {
      background: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
    }

    /* 報名方式篩選按鈕列 (純粹切換 需報名 / 不需報名) */
    .apply-filter-row {
      display: flex;
      gap: 6px;
    }
    .apply-btn {
      flex: 1;
      padding: 6px 8px;
      border-radius: 8px;
      border: 1.5px solid #cbd5e1;
      background: #ffffff;
      color: #475569;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      transition: all 0.2s ease;
      white-space: nowrap;
    }
    .apply-btn:hover {
      background: #f1f5f9;
      color: #0f172a;
    }
    .apply-btn.active {
      background: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
      box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
    }
    .apply-btn[data-apply="需報名"].active {
      background: #dc2626;
      border-color: #dc2626;
      box-shadow: 0 2px 6px rgba(220, 38, 38, 0.25);
    }
    .apply-btn[data-apply="不需報名"].active {
      background: #16a34a;
      border-color: #16a34a;
      box-shadow: 0 2px 6px rgba(22, 163, 74, 0.25);
    }

    /* 下拉篩選選單列 */
    .dropdown-row {
      display: flex;
      gap: 6px;
    }
    .custom-select {
      flex: 1;
      padding: 6px 8px;
      border-radius: 6px;
      border: 1.5px solid #cbd5e1;
      font-size: 11.5px;
      font-weight: 600;
      background: #f8fafc;
      color: #334155;
      outline: none;
      cursor: pointer;
    }
    .custom-select:focus {
      border-color: var(--primary);
      background: #ffffff;
    }

    /* 篩選結果統計資訊列 */
    .filter-summary-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 14px;
      background: #f1f5f9;
      border-bottom: 1px solid #e2e8f0;
      font-size: 12px;
      font-weight: 700;
      color: #475569;
    }

    /* 活動列表滾動容器 */
    .event-list-container {
      flex: 1;
      overflow-y: auto;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      background: #f8fafc;
    }

    /* 活動卡片樣式 */
    .event-card {
      background: #ffffff;
      border: 1.5px solid var(--border-color);
      border-radius: 12px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
      transition: all 0.2s ease;
    }
    .event-card:hover {
      border-color: #94a3b8;
      box-shadow: 0 6px 16px rgba(37, 99, 235, 0.1);
      transform: translateY(-2px);
    }
    .event-card.active {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2), 0 8px 20px rgba(37, 99, 235, 0.15);
      background: #ffffff;
    }

    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
    }
    .card-title {
      font-size: 14px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.35;
      flex: 1;
    }
    .theme-pill {
      font-size: 10px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 4px;
      white-space: nowrap;
      flex-shrink: 0;
    }
    .theme-kids { background: #fef3c7; color: #b45309; }
    .theme-open { background: #e0f2fe; color: #0369a1; }
    .theme-south { background: #dcfce7; color: #15803d; }

    .card-organizer {
      font-size: 12px;
      font-weight: 600;
      color: #475569;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .card-meta-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 2px;
    }
    .meta-tag {
      font-size: 11px;
      font-weight: 600;
      background: #f1f5f9;
      color: #475569;
      padding: 2px 7px;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap !important;
      flex-shrink: 0 !important;
    }
    .meta-tag.tag-walkin {
      background: #f1f5f9;
      color: #475569;
      font-weight: 600;
      border: 1px solid #e2e8f0;
      white-space: nowrap !important;
      flex-shrink: 0 !important;
    }
    .meta-tag.tag-needapply {
      background: #eff6ff;
      color: #2563eb;
      font-weight: 700;
      border: 1px solid #bfdbfe;
      white-space: nowrap !important;
      flex-shrink: 0 !important;
    }
    .meta-tag.tag-reg-stat {
      background: #eff6ff;
      color: #1e40af;
      border: 1px solid #bfdbfe;
      font-weight: 700;
      white-space: nowrap !important;
      flex-shrink: 0 !important;
      padding: 2.5px 7px;
      border-radius: 5px;
      line-height: 1.2;
    }
    .meta-tag.tag-reg-stat b {
      font-weight: 800;
    }
    .meta-tag.tag-reg-stat.overbooked {
      background: #fef2f2;
      color: #b91c1c;
      border-color: #fecaca;
    }
    .meta-tag.tag-reg-stat.available {
      background: #f0fdf4;
      color: #15803d;
      border-color: #bbf7d0;
    }

    .card-location {
      font-size: 11.5px;
      color: #64748b;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #f8fafc;
      padding: 5px 8px;
      border-radius: 6px;
      border: 1px solid #f1f5f9;
    }

    /* 精緻極簡 RWD 場次列表 */
    .session-list-wrapper {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      overflow: hidden;
      margin-top: 3px;
    }
    .session-row-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4.5px 8px;
      border-bottom: 1px solid #edf2f7;
      font-size: 11px;
      gap: 6px;
      transition: background 0.15s;
    }
    .session-row-item:last-child {
      border-bottom: none;
    }
    .session-row-item:hover {
      background: #f1f5f9;
    }
    .session-time-col {
      font-weight: 700;
      color: #334155;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .session-time-col i {
      color: #2563eb;
      font-size: 10px;
    }
    .session-stat-mini {
      font-size: 10px;
      font-weight: 800;
      padding: 1.5px 6px;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      gap: 3.5px;
      white-space: nowrap;
      flex-shrink: 0;
    }
    .session-stat-mini.overbooked {
      background: #fee2e2;
      color: #b91c1c;
      border: 1px solid #fca5a5;
    }
    .session-stat-mini.available {
      background: #dcfce7;
      color: #15803d;
      border: 1px solid #86efac;
    }
    .session-stat-mini .dot {
      width: 5px;
      height: 5px;
      border-radius: 50%;
      display: inline-block;
    }
    .session-stat-mini.overbooked .dot { background: #ef4444; }
    .session-stat-mini.available .dot { background: #22c55e; }

    /* 展開/收合多場次按鈕 */
    .toggle-sessions-btn {
      width: 100%;
      background: #f1f5f9;
      border: none;
      border-top: 1px dashed #cbd5e1;
      padding: 4px 8px;
      font-size: 10.5px;
      font-weight: 700;
      color: #475569;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      transition: background 0.15s;
    }
    .toggle-sessions-btn:hover {
      background: #e2e8f0;
      color: #0f172a;
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 4px;
      padding-top: 6px;
      border-top: 1px solid #f1f5f9;
    }
    .card-footer-actions {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .card-link {
      font-size: 11.5px;
      font-weight: 800;
      color: #2563eb;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .card-link:hover {
      text-decoration: underline;
    }

    .card-link-reg {
      font-size: 11px;
      font-weight: 800;
      color: #4338ca;
      background: #eef2ff;
      border: 1px solid #c7d2fe;
      padding: 2px 7px;
      border-radius: 5px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 3.5px;
      transition: all 0.15s ease;
    }
    .card-link-reg:hover {
      background: #4338ca;
      color: #ffffff;
      border-color: #4338ca;
    }

    /* 設施專用卡片 */
    .facility-card {
      background: #ffffff !important;
      border: 1.5px solid #cbd5e1;
      border-left: 5px solid #64748b;
      border-radius: 12px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.04);
      transition: all 0.2s ease;
    }
    .facility-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.08);
      border-color: #94a3b8;
    }
    .facility-card.fac-接待與服務 { border-left-color: #ea580c !important; }
    .facility-card.fac-餐飲資訊 { border-left-color: #dc2626 !important; }
    .facility-card.fac-休憩場所 { border-left-color: #16a34a !important; }
    .facility-card.fac-哺集乳室 { border-left-color: #9333ea !important; }
    .facility-card.fac-洗手間 { border-left-color: #0284c7 !important; }
    .facility-card.fac-箱水及飲水機 { border-left-color: #0891b2 !important; }
    .facility-card.fac-免費接駁車 { border-left-color: #d97706 !important; }
    .facility-card.fac-停車與交通資訊 { border-left-color: #475569 !important; }

    /* 右側地圖面板 */
    .map-panel {
      flex: 1;
      position: relative;
      height: 100%;
    }
    #map {
      width: 100%;
      height: 100%;
      background: #e2e8f0;
    }

    /* 院區快速切換懸浮按鈕 */
    .campus-switch-bar {
      position: absolute;
      top: 14px;
      left: 14px;
      z-index: 500;
      display: flex;
      gap: 8px;
    }
    .campus-btn {
      background: #ffffff;
      color: #0f172a;
      border: 1.5px solid #cbd5e1;
      padding: 7px 13px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s ease;
      user-select: none;
    }
    .campus-btn.active {
      background: #0f172a !important;
      color: #ffffff !important;
      border-color: #0f172a !important;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.25) !important;
    }
    .campus-btn:hover {
      background: #f1f5f9;
      color: #0f172a;
      border-color: #94a3b8;
    }
    .campus-btn.active:hover {
      background: #0f172a;
      color: #ffffff;
    }

    /* 大樓活動數字圖釘 */
    .building-pin {
      position: relative;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff !important;
      font-weight: 900 !important;
      font-size: 13px !important;
      line-height: 1;
      box-shadow: 0 4px 12px rgba(0,0,0,0.35);
      border: 2px solid #ffffff;
      transition: transform 0.2s ease;
      user-select: none;
    }
    .building-pin:hover {
      transform: scale(1.25);
    }
    .building-pin .num {
      color: #ffffff !important;
      font-weight: 900 !important;
      font-size: 13px !important;
      display: block !important;
      text-shadow: 0 1px 2px rgba(0,0,0,0.4);
    }
    .building-pin::after {
      content: '';
      position: absolute;
      left: 50%;
      bottom: -7px;
      transform: translateX(-50%);
      border-left: 5px solid transparent;
      border-right: 5px solid transparent;
      border-top: 7px solid #2563eb;
    }
    .building-pin.blue   { background: #2563eb !important; }
    .building-pin.blue::after { border-top-color: #2563eb !important; }
    .building-pin.orange { background: #ea580c !important; }
    .building-pin.orange::after { border-top-color: #ea580c !important; }
    .building-pin.red    { background: #dc2626 !important; }
    .building-pin.red::after { border-top-color: #dc2626 !important; }

    /* 設施圖釘與 Badge 樣式 */
    .facility-pin {
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      color: #ffffff;
      font-size: 13px;
      box-shadow: 0 3px 10px rgba(0,0,0,0.35);
      border: 2px solid #ffffff;
      transition: transform 0.2s;
    }
    .facility-pin:hover {
      transform: scale(1.25);
    }
    .facility-pin.fac-接待與服務, .popup-badge.fac-接待與服務 { background: #ea580c !important; }
    .facility-pin.fac-餐飲資訊, .popup-badge.fac-餐飲資訊 { background: #dc2626 !important; }
    .facility-pin.fac-休憩場所, .popup-badge.fac-休憩場所 { background: #16a34a !important; }
    .facility-pin.fac-哺集乳室, .popup-badge.fac-哺集乳室 { background: #9333ea !important; }
    .facility-pin.fac-洗手間, .popup-badge.fac-洗手間 { background: #0284c7 !important; }
    .facility-pin.fac-箱水及飲水機, .popup-badge.fac-箱水及飲水機 { background: #0891b2 !important; }
    .facility-pin.fac-免費接駁車, .popup-badge.fac-免費接駁車 { background: #d97706 !important; }
    .facility-pin.fac-停車與交通資訊, .popup-badge.fac-停車與交通資訊 { background: #475569 !important; }

    /* Popup 彈窗樣式 */
    .leaflet-popup-content-wrapper {
      background: #ffffff !important;
      color: #0f172a !important;
      border-radius: 14px !important;
      padding: 0 !important;
      overflow: hidden;
      box-shadow: 0 12px 32px rgba(0,0,0,0.2) !important;
      border: 1px solid #e2e8f0;
    }
    .leaflet-popup-content {
      margin: 0 !important;
      line-height: 1.5;
      font-size: 12.5px;
      max-height: 420px;
      overflow-y: auto;
      width: 330px !important;
    }
    .popup-box {
      padding: 12px 14px;
    }
    .popup-title {
      font-size: 15px;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 6px;
      line-height: 1.35;
    }
    .popup-badge {
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      margin-bottom: 8px;
    }
    .popup-desc {
      font-size: 12px;
      color: #475569;
      margin-top: 4px;
      line-height: 1.5;
    }

    /* 手機版懸浮按鈕 */
    .mobile-filter-fab {
      display: none;
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 500;
      background: linear-gradient(135deg, #0f172a, #1e293b);
      color: #ffffff;
      padding: 10px 22px;
      border-radius: 30px;
      font-size: 13.5px;
      font-weight: 800;
      border: 1.5px solid #475569;
      box-shadow: 0 8px 24px rgba(0,0,0,0.35);
      cursor: pointer;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
      transition: all 0.2s;
    }

    .mobile-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(2px);
      z-index: 590;
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    .mobile-backdrop.active {
      display: block;
      opacity: 1;
    }

    .sidebar-drawer-header {
      display: none;
      justify-content: space-between;
      align-items: center;
      padding: 12px 14px;
      border-bottom: 1.5px solid var(--border-color);
      background: #ffffff;
    }
    .drawer-close-btn {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      color: #475569;
      font-size: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .drawer-close-btn:hover {
      background: #e2e8f0;
      color: #0f172a;
    }

    @media (max-width: 768px) {
      .app-header {
        height: auto;
        padding: 8px 12px 6px 12px;
        flex-direction: column;
        align-items: stretch;
        gap: 6px;
      }
      .header-brand h1 {
        font-size: 14px;
      }
      .header-layers-bar {
        display: flex !important;
        overflow-x: auto;
        padding: 2px 0 2px 0;
        gap: 5px;
        -webkit-overflow-scrolling: touch;
      }
      .layer-chip {
        padding: 3px 7px;
        font-size: 10.5px;
      }
      .header-reg-btn {
        padding: 4px 9px;
        font-size: 11px;
      }
      .sidebar-drawer-header {
        display: flex !important;
      }
      .sidebar-panel {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        width: 90vw;
        max-width: 390px;
        border-radius: 0 16px 16px 0;
        box-shadow: 8px 0 32px rgba(0,0,0,0.3);
        z-index: 600;
        transform: translateX(-100%);
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        overscroll-behavior: contain;
      }
      .sidebar-panel.open {
        transform: translateX(0);
      }

      .leaflet-bottom.leaflet-right {
        bottom: 68px !important;
        right: 12px !important;
      }
      .leaflet-control-zoom {
        border: none !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
      }

      .mobile-filter-fab {
        display: inline-flex !important;
        position: fixed !important;
        bottom: 16px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        padding: 9px 18px !important;
        font-size: 12.5px !important;
        font-weight: 800 !important;
        z-index: 900 !important;
        border-radius: 30px !important;
        background: #0f172a !important;
        color: #ffffff !important;
        border: 1.5px solid #334155 !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.35) !important;
        white-space: nowrap !important;
        align-items: center !important;
        gap: 6px !important;
      }
      .campus-switch-bar {
        top: 8px;
        left: 8px;
        gap: 6px;
      }
      .campus-btn {
        padding: 5px 9px;
        font-size: 10.5px;
        border-radius: 20px;
        background: #ffffff;
        color: #0f172a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
      }
      .campus-btn.active {
        background: #0f172a !important;
        color: #ffffff !important;
        border-color: #0f172a !important;
      }
      .leaflet-popup-content {
        max-width: calc(100vw - 28px) !important;
        width: min(330px, calc(100vw - 28px)) !important;
        max-height: 380px;
      }
    }
  </style>
</head>
<body>

  <!-- 頂部導航列 -->
  <header class="app-header">
    <div style="display:flex; align-items:center; gap:12px;">
      <div class="header-brand">
        <div class="brand-icon">
          <i class="fa-solid fa-map-location-dot"></i>
        </div>
        <div class="brand-text">
          <h1>中研院 2026 Openhouse 活動地圖</h1>
        </div>
      </div>
      <a href="../%E5%A0%B1%E5%90%8D%E5%88%86%E6%9E%90/index.html" target="_blank" class="header-reg-btn" title="查看全院即時報名人數與錄取率分析">
        <i class="fa-solid fa-chart-pie"></i>
        <span>報名戰況看板</span>
        <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 10px;"></i>
      </a>
    </div>

    <!-- 頂部圖層控制列 (支援手機橫向滑動) -->
    <div class="header-layers-bar" id="headerLayersBar">
      <div class="layer-chip active" data-layer="events" onclick="toggleLayer('events', this)">
        <i class="fa-solid fa-calendar-days"></i> 2026活動 (259)
      </div>
      <div class="layer-chip" data-layer="接待與服務" onclick="toggleLayer('接待與服務', this)">
        <i class="fa-solid fa-circle-info"></i> 接待服務
      </div>
      <div class="layer-chip" data-layer="餐飲資訊" onclick="toggleLayer('餐飲資訊', this)">
        <i class="fa-solid fa-utensils"></i> 餐飲美食
      </div>
      <div class="layer-chip" data-layer="休憩場所" onclick="toggleLayer('休憩場所', this)">
        <i class="fa-solid fa-couch"></i> 休憩場所
      </div>
      <div class="layer-chip" data-layer="哺集乳室" onclick="toggleLayer('哺集乳室', this)">
        <i class="fa-solid fa-baby"></i> 哺集乳室
      </div>
      <div class="layer-chip" data-layer="洗手間" onclick="toggleLayer('洗手間', this)">
        <i class="fa-solid fa-restroom"></i> 洗手間
      </div>
      <div class="layer-chip" data-layer="箱水及飲水機" onclick="toggleLayer('箱水及飲水機', this)">
        <i class="fa-solid fa-bottle-water"></i> 箱水及飲水機
      </div>
      <div class="layer-chip" data-layer="免費接駁車" onclick="toggleLayer('免費接駁車', this)">
        <i class="fa-solid fa-van-shuttle"></i> 免費接駁車
      </div>
      <div class="layer-chip" data-layer="停車與交通資訊" onclick="toggleLayer('停車與交通資訊', this)">
        <i class="fa-solid fa-square-parking"></i> 停車與交通
      </div>
    </div>
  </header>

  <!-- 主畫面 -->
  <main class="app-main">
    
    <!-- 手機版側邊欄遮罩 -->
    <div class="mobile-backdrop" id="mobileBackdrop" onclick="closeMobileDrawer()"></div>

    <!-- 左側側邊欄 -->
    <div class="sidebar-panel" id="sidebarPanel">
      
      <!-- 手機版抽屜頂部標題與關閉按鈕 -->
      <div class="sidebar-drawer-header">
        <div style="display:flex; align-items:center; gap:8px;">
          <div class="brand-icon" style="width:26px; height:26px; font-size:12px;"><i class="fa-solid fa-sliders"></i></div>
          <span style="font-size:14px; font-weight:800; color:#0f172a;">活動篩選與清單</span>
        </div>
        <button class="drawer-close-btn" onclick="closeMobileDrawer()" aria-label="關閉清單">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      
      <!-- 篩選區域 -->
      <div class="sidebar-filters">
        
        <!-- 搜尋列 -->
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" id="searchInput" class="search-input" placeholder="搜尋活動名稱、講者、主題或館舍..." oninput="applyFilters()">
        </div>

        <!-- 活動主題切換列 -->
        <div class="theme-card-row" id="themeChips">
          <div class="theme-card-chip active" data-theme="ALL" onclick="setThemeFilter('ALL', this)">🎪 全部活動 (259)</div>
          <div class="theme-card-chip" data-theme="兒童科普日" onclick="setThemeFilter('兒童科普日', this)">👶 10/3 兒童科普日 (58)</div>
          <div class="theme-card-chip" data-theme="院區開放日" onclick="setThemeFilter('院區開放日', this)">🏛️ 10/17 院區開放日 (166)</div>
          <div class="theme-card-chip" data-theme="南部院區開放日" onclick="setThemeFilter('南部院區開放日', this)">🌴 11/14 南部院區 (35)</div>
        </div>

        <!-- 報名方式切換列 (純粹切換 需報名 / 不需報名) -->
        <div class="apply-filter-row" id="applyChips">
          <button type="button" class="apply-btn active" data-apply="ALL" onclick="setApplyFilter('ALL', this)">
            <i class="fa-solid fa-layer-group"></i> 全部方式
          </button>
          <button type="button" class="apply-btn" data-apply="需報名" onclick="setApplyFilter('需報名', this)">
            <i class="fa-solid fa-ticket"></i> 需報名
          </button>
          <button type="button" class="apply-btn" data-apply="不需報名" onclick="setApplyFilter('不需報名', this)">
            <i class="fa-solid fa-door-open"></i> 不需報名 (隨到隨玩)
          </button>
        </div>

        <!-- 活動組別與類型下拉選單 -->
        <div class="dropdown-row">
          <select id="groupSelect" class="custom-select" onchange="applyFilters()">
            <option value="ALL">全部學術組別</option>
            <option value="數理科學">數理科學組</option>
            <option value="生命科學">生命科學組</option>
            <option value="人文及社會科學">人文社會組</option>
            <option value="院本部">院本部/其他</option>
          </select>
          <select id="typeSelect" class="custom-select" onchange="applyFilters()">
            <option value="ALL">全部活動類型</option>
            <option value="參觀導覽">參觀導覽</option>
            <option value="演講座談">演講座談</option>
            <option value="互動體驗">互動體驗</option>
            <option value="成果展示">成果展示</option>
            <option value="影片欣賞">影片欣賞</option>
          </select>
        </div>

        <!-- 時間區間篩選 -->
        <div class="dropdown-row">
          <select id="timeStartSelect" class="custom-select" onchange="applyFilters()">
            <option value="ALL">🕒 開始時間 (不限)</option>
            <option value="08:00">08:00 以後</option>
            <option value="09:00">09:00 以後</option>
            <option value="10:00">10:00 以後</option>
            <option value="11:00">11:00 以後</option>
            <option value="12:00">12:00 以後</option>
            <option value="13:00">13:00 以後</option>
            <option value="14:00">14:00 以後</option>
            <option value="15:00">15:00 以後</option>
            <option value="16:00">16:00 以後</option>
            <option value="17:00">17:00 以後</option>
          </select>
          <select id="timeEndSelect" class="custom-select" onchange="applyFilters()">
            <option value="ALL">🕒 結束時間 (不限)</option>
            <option value="10:00">10:00 以前</option>
            <option value="11:00">11:00 以前</option>
            <option value="12:00">12:00 以前</option>
            <option value="13:00">13:00 以前</option>
            <option value="14:00">14:00 以前</option>
            <option value="15:00">15:00 以前</option>
            <option value="16:00">16:00 以前</option>
            <option value="17:00">17:00 以前</option>
            <option value="18:00">18:00 以前</option>
          </select>
        </div>
      </div>

      <!-- 統計資訊列 -->
      <div class="filter-summary-bar">
        <span>符合條件活動：<strong id="filterTotalCount" style="color:#2563eb;">259</strong> 場</span>
        <span style="font-size:11px; color:#94a3b8;">點擊卡片可聚焦地圖</span>
      </div>

      <!-- 活動卡片清單列表 -->
      <div class="event-list-container" id="cardsContainer">
        <!-- 卡片由 JS 動態生成 -->
      </div>
    </div>

    <!-- 右側地圖區域 -->
    <div class="map-panel">
      
      <!-- 院區切換懸浮列 -->
      <div class="campus-switch-bar">
        <button id="btnCampusNankang" class="campus-btn active" onclick="flyToCampus('nankang')">
          <i class="fa-solid fa-landmark"></i> 南港總院區
        </button>
        <button id="btnCampusSouth" class="campus-btn" onclick="flyToCampus('south')">
          <i class="fa-solid fa-tree"></i> 台南南部院區
        </button>
      </div>

      <!-- Leaflet 地圖容器 -->
      <div id="map"></div>

      <!-- 手機版懸浮開啟清單按鈕 -->
      <button class="mobile-filter-fab" onclick="openMobileDrawer()">
        <i class="fa-solid fa-list-ul"></i>
        <span>查看活動清單 (<span id="mobileCountBadge">259</span>)</span>
      </button>
    </div>
  </main>

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

  <script>
    const allEventsData = __EVENTS_JSON__;
    const allFacilitiesData = __FACILITIES_JSON__;
    const allRegistrationData = __REGISTRATION_JSON__;

    // 建立正規化輔助函式
    function normalizeTitle(s) {
      if (!s) return '';
      return s.replace(/[\\s\\u3000\\u00a0\\u30fb\\u00b7\\u2014\\u2500\\uff0d\\-:：!！\\?？\\.,，\\(\\)（）\\-_—]+/g, '').toLowerCase();
    }

    // 簡化時間字串，避免 RWD 換行破版 (例如: "10/03 09:00 -10/03 09:50" -> "10/03 09:00~09:50")
    function formatCleanTime(timeStr) {
      if (!timeStr) return '依現場公告';
      let clean = timeStr.trim();
      clean = clean.replace(/(\\d{1,2}\\/\\d{1,2})\\s*(\\d{1,2}:\\d{2})\\s*-\\s*\\1\\s*(\\d{1,2}:\\d{2})/, '$1 $2~$3');
      clean = clean.replace(/\\s*-\\s*/, '~');
      return clean;
    }

    // 提取時間關鍵字 (MM/DD 與 HH:MM)
    function extractTimeKeys(timeStr) {
      if (!timeStr) return { date: '', start: '' };
      let dateKey = '';
      const mDate = timeStr.match(/(\\d{1,2}\\/\\d{1,2})/);
      if (mDate) {
        const parts = mDate[1].split('/');
        dateKey = `${parts[0].padStart(2, '0')}/${parts[1].padStart(2, '0')}`;
      } else {
        const mFullDate = timeStr.match(/(\\d{4}-\\d{2}-\\d{2})/);
        if (mFullDate) {
          const parts = mFullDate[1].split('-');
          dateKey = `${parts[1].padStart(2, '0')}/${parts[2].padStart(2, '0')}`;
        }
      }

      let startKey = '';
      const mTimes = timeStr.match(/(\\d{1,2}:\\d{2})/g);
      if (mTimes && mTimes.length > 0) {
        startKey = mTimes[0].padStart(5, '0');
      }

      return { date: dateKey, start: startKey };
    }

    // 建立報名資料快速查找字典
    const regLookup = new Map();
    (allRegistrationData || []).forEach(r => {
      const k = normalizeTitle(r.activity);
      if (!regLookup.has(k)) {
        regLookup.set(k, []);
      }
      regLookup.get(k).push(r);
    });

    // 計算每個活動的報名狀態與「已報名人數 / 名額」
    function getEventRegistrationInfo(ev) {
      if (ev.need_apply !== '需報名') {
        return {
          status: 'walk_in',
          label: '不需報名',
          hasStats: false,
          sessions: []
        };
      }

      const norm = normalizeTitle(ev.title);
      let list = regLookup.get(norm);
      if (!list || list.length === 0) {
        for (const [k, items] of regLookup.entries()) {
          if (k.includes(norm) || norm.includes(k)) {
            list = items;
            break;
          }
        }
      }

      if (!list || list.length === 0) {
        return {
          status: 'need_apply',
          label: '需報名',
          hasStats: false,
          sessions: []
        };
      }

      let totalLimit = 0;
      let totalWait = 0;
      let totalRemain = 0;
      let hasOverbooked = false;

      list.forEach(item => {
        const lim = item.limit || 0;
        const wt = item.wait || 0;
        totalLimit += lim;
        totalWait += wt;
        totalRemain += (item.remain || 0);
        if (lim > 0 && wt > lim) {
          hasOverbooked = true;
        }
      });

      return {
        status: 'need_apply',
        hasStats: true,
        totalLimit: totalLimit,
        totalWait: totalWait,
        totalRemain: totalRemain,
        isOverbooked: hasOverbooked,
        sessions: list
      };
    }

    // 為特定場次找出精確的報名數據
    function getSessionRegistrationStat(ev, sessionObj, sessionIndex) {
      const regInfo = ev.regInfo;
      if (!regInfo || !regInfo.hasStats || !regInfo.sessions || regInfo.sessions.length === 0) {
        return null;
      }

      const regItems = regInfo.sessions;
      const sTimeKeys = extractTimeKeys(sessionObj.time || '');

      // 1. 優先比對日期 + 開始時間
      if (sTimeKeys.date && sTimeKeys.start) {
        const matched = regItems.find(r => {
          const rTimeKeys = extractTimeKeys(r.raw_time || '');
          return rTimeKeys.date === sTimeKeys.date && rTimeKeys.start === sTimeKeys.start;
        });
        if (matched) return matched;
      }

      // 2. 比對開始時間 (若日期略有不同)
      if (sTimeKeys.start) {
        const matched = regItems.find(r => {
          const rTimeKeys = extractTimeKeys(r.raw_time || '');
          return rTimeKeys.start === sTimeKeys.start;
        });
        if (matched) return matched;
      }

      // 3. 比對場次名稱
      const sNorm = normalizeTitle(sessionObj.session_name);
      if (sNorm) {
        const matched = regItems.find(r => {
          const rNorm = normalizeTitle(r.session);
          return rNorm === sNorm || rNorm.includes(sNorm) || sNorm.includes(rNorm);
        });
        if (matched) return matched;
      }

      // 4. 場次數量一致時，依序號對應
      if (regItems.length === (ev.sessions || []).length && regItems[sessionIndex]) {
        return regItems[sessionIndex];
      }

      // 5. 單場次對應
      if (regItems.length === 1) {
        return regItems[0];
      }

      return null;
    }

    // 為所有活動預先計算報名狀態
    allEventsData.forEach(ev => {
      ev.regInfo = getEventRegistrationInfo(ev);
    });

    const facilityIconConfig = {
      '接待與服務': { icon: 'fa-circle-info', color: '#ea580c' },
      '餐飲資訊': { icon: 'fa-utensils', color: '#dc2626' },
      '休憩場所': { icon: 'fa-couch', color: '#16a34a' },
      '哺集乳室': { icon: 'fa-baby', color: '#9333ea' },
      '洗手間': { icon: 'fa-restroom', color: '#0284c7' },
      '箱水及飲水機': { icon: 'fa-bottle-water', color: '#0891b2' },
      '免費接駁車': { icon: 'fa-van-shuttle', color: '#d97706' },
      '停車與交通資訊': { icon: 'fa-square-parking', color: '#475569' }
    };

    const map = L.map('map', {
      zoomControl: false,
      maxZoom: 19,
      minZoom: 13
    }).setView([25.0418, 121.6145], 16);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const layerGroupMap = {
      events: L.layerGroup().addTo(map),
      '接待與服務': L.layerGroup(),
      '餐飲資訊': L.layerGroup(),
      '休憩場所': L.layerGroup(),
      '哺集乳室': L.layerGroup(),
      '洗手間': L.layerGroup(),
      '箱水及飲水機': L.layerGroup(),
      '免費接駁車': L.layerGroup(),
      '停車與交通資訊': L.layerGroup()
    };

    const activeLayers = new Set(['events']);
    let currentThemeFilter = 'ALL';
    let lastNankangTheme = 'ALL';
    let currentApplyFilter = 'ALL';

    function createBuildingPin(count) {
      let colorClass = 'blue';
      if (count >= 10) colorClass = 'red';
      else if (count >= 5) colorClass = 'orange';

      return L.divIcon({
        className: 'custom-div-icon',
        html: `<div class="building-pin ${colorClass}"><span class="num">${count}</span></div>`,
        iconSize: [32, 39],
        iconAnchor: [16, 39],
        popupAnchor: [0, -36]
      });
    }

    function createFacilityPin(category) {
      const cfg = facilityIconConfig[category] || { icon: 'fa-location-dot', color: '#475569' };
      return L.divIcon({
        className: 'custom-div-icon',
        html: `<div class="facility-pin fac-${category}" style="width:28px; height:28px; font-size:12px;"><i class="fa-solid ${cfg.icon}"></i></div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -14]
      });
    }

    function setApplyFilter(val, el) {
      currentApplyFilter = val;
      document.querySelectorAll('.apply-btn').forEach(b => b.classList.remove('active'));
      if (el) el.classList.add('active');
      applyFilters();
    }

    // 展開 / 收合過多場次
    function toggleSessions(containerId, btn) {
      const hiddenPart = document.getElementById(containerId);
      if (!hiddenPart) return;
      if (hiddenPart.style.display === 'none' || hiddenPart.style.display === '') {
        hiddenPart.style.display = 'block';
        btn.innerHTML = '收合部分場次 <i class="fa-solid fa-chevron-up"></i>';
      } else {
        hiddenPart.style.display = 'none';
        const total = btn.getAttribute('data-total') || '';
        btn.innerHTML = `展開其餘場次 (共 ${total} 場) <i class="fa-solid fa-chevron-down"></i>`;
      }
    }

    // 生成緊湊 RWD 場次列表 HTML (共用於卡片與彈窗)
    function renderCompactSessionsHtml(ev, isPopup = false) {
      const sessions = ev.sessions || [];
      if (sessions.length === 0) {
        return '<div style="color: #64748b; font-size: 11px; padding: 4px;"><i class="fa-regular fa-clock"></i> 時間依現場公告</div>';
      }

      const limitVisible = isPopup ? 3 : 3;
      const visibleSessions = sessions.slice(0, limitVisible);
      const hiddenSessions = sessions.slice(limitVisible);
      const uniqueId = `sess_${ev.event_id}_${isPopup ? 'pop' : 'card'}`;

      function renderRow(s, idx) {
        const cleanTime = formatCleanTime(s.time);
        const matchedStat = getSessionRegistrationStat(ev, s, idx);

        let statHtml = '';
        if (matchedStat && matchedStat.limit > 0) {
          const isOver = matchedStat.wait > matchedStat.limit;
          statHtml = `
            <span class="session-stat-mini ${isOver ? 'overbooked' : 'available'}" title="本場已報名 ${matchedStat.wait} 人 / 限額 ${matchedStat.limit} 人">
              <span class="dot"></span>${matchedStat.wait}/${matchedStat.limit}人
            </span>
          `;
        }

        const extraName = (s.session_name && s.session_name !== ev.title)
          ? `<span style="color:#64748b; font-size:10px; margin-left:4px;">(${s.session_name})</span>`
          : '';

        return `
          <div class="session-row-item">
            <div class="session-time-col" title="${cleanTime}">
              <i class="fa-regular fa-clock"></i>
              <span>${cleanTime}</span>
              ${extraName}
            </div>
            ${statHtml}
          </div>
        `;
      }

      let html = '<div class="session-list-wrapper">';
      visibleSessions.forEach((s, idx) => {
        html += renderRow(s, idx);
      });

      if (hiddenSessions.length > 0) {
        html += `<div id="${uniqueId}" style="display:none;">`;
        hiddenSessions.forEach((s, idx) => {
          html += renderRow(s, limitVisible + idx);
        });
        html += `</div>`;
        html += `
          <button type="button" class="toggle-sessions-btn" data-total="${sessions.length}" onclick="event.stopPropagation(); toggleSessions('${uniqueId}', this)">
            展開其餘場次 (共 ${sessions.length} 場) <i class="fa-solid fa-chevron-down"></i>
          </button>
        `;
      }

      html += '</div>';
      return html;
    }

    function applyFilters() {
      const searchText = (document.getElementById('searchInput')?.value || '').trim().toLowerCase();
      const groupFilter = document.getElementById('groupSelect')?.value || 'ALL';
      const typeFilter = document.getElementById('typeSelect')?.value || 'ALL';
      const timeStart = document.getElementById('timeStartSelect')?.value || 'ALL';
      const timeEnd = document.getElementById('timeEndSelect')?.value || 'ALL';

      const cardsContainer = document.getElementById('cardsContainer');
      if (!cardsContainer) return;
      cardsContainer.innerHTML = '';

      Object.values(layerGroupMap).forEach(lg => lg.clearLayers());

      const matchedEvents = allEventsData.filter(ev => {
        if (currentThemeFilter !== 'ALL') {
          if (currentThemeFilter === '南部院區開放日') {
            if (!(ev.theme || '').startsWith('南')) return false;
          } else {
            if (ev.theme !== currentThemeFilter) return false;
          }
        }

        if (groupFilter !== 'ALL' && (ev.group_name || '') !== groupFilter) return false;
        if (typeFilter !== 'ALL' && (ev.event_type || '') !== typeFilter) return false;

        // 報名方式篩選 (需報名 vs 不需報名)
        if (currentApplyFilter !== 'ALL') {
          if (currentApplyFilter === '需報名') {
            if (ev.need_apply !== '需報名') return false;
          } else if (currentApplyFilter === '不需報名') {
            if (ev.need_apply === '需報名') return false;
          }
        }

        if (timeStart !== 'ALL' || timeEnd !== 'ALL') {
          const sessions = ev.sessions || [];
          if (sessions.length === 0) return false;

          const matchSession = sessions.some(s => {
            const times = (s.time || '').match(/\\d{1,2}:\\d{2}/g);
            if (times && times.length >= 2) {
              const sStart = times[0].padStart(5, '0');
              const sEnd = times[1].padStart(5, '0');
              if (timeStart !== 'ALL' && sStart < timeStart) return false;
              if (timeEnd !== 'ALL' && sEnd > timeEnd) return false;
              return true;
            }
            return false;
          });
          if (!matchSession) return false;
        }

        if (searchText) {
          if (searchText === '需報名') {
            if (ev.need_apply !== '需報名') return false;
          } else if (searchText === '不需報名' || searchText === '免報名') {
            if (ev.need_apply === '需報名') return false;
          } else {
            const targetStr = `${ev.title} ${ev.organizer} ${ev.location} ${ev.speaker} ${ev.description} ${ev.notes} ${ev.event_id} ${ev.need_apply || ''} ${ev.event_type || ''} ${ev.target || ''} ${ev.group_name || ''} ${ev.theme || ''}`.toLowerCase();
            if (!targetStr.includes(searchText)) return false;
          }
        }

        return true;
      });

      const totalCountEl = document.getElementById('filterTotalCount');
      if (totalCountEl) totalCountEl.innerText = matchedEvents.length;

      const mobileCountEl = document.getElementById('mobileCountBadge');
      if (mobileCountEl) mobileCountEl.innerText = matchedEvents.length;

      if (activeLayers.has('events')) {
        if (layerGroupMap['events'] && !map.hasLayer(layerGroupMap['events'])) {
          layerGroupMap['events'].addTo(map);
        }

        const buildingMap = new Map();
        const buildingMarkersMap = new Map();
        matchedEvents.forEach(ev => {
          if (!ev.lat || !ev.lng) return;
          const lat = parseFloat(ev.lat);
          const lng = parseFloat(ev.lng);
          if (isNaN(lat) || isNaN(lng)) return;

          const key = `${lat.toFixed(4)},${lng.toFixed(4)}`;
          if (!buildingMap.has(key)) {
            buildingMap.set(key, {
              lat: lat,
              lng: lng,
              locationName: ev.location || '活動地點',
              events: []
            });
          }
          buildingMap.get(key).events.push(ev);
        });

        buildingMap.forEach((bData, key) => {
          const count = bData.events.length;
          const marker = L.marker([bData.lat, bData.lng], { icon: createBuildingPin(count) });
          buildingMarkersMap.set(key, marker);

          const eventItemsHtml = bData.events.map(e => {
            const regInfo = e.regInfo || { status: 'walk_in', hasStats: false };

            let applyTagHtml = '';
            if (e.need_apply === '需報名') {
              if (regInfo.hasStats && regInfo.totalLimit > 0) {
                const statClass = regInfo.isOverbooked ? 'overbooked' : 'available';
                applyTagHtml = `<span class="meta-tag tag-reg-stat ${statClass}" title="全場累計已報名 ${regInfo.totalWait} 人 / 總限額 ${regInfo.totalLimit} 人"><i class="fa-solid fa-users"></i> 報名 <b>${regInfo.totalWait}</b> / 名額 <b>${regInfo.totalLimit}</b></span>`;
              } else {
                applyTagHtml = `<span class="meta-tag tag-needapply"><i class="fa-solid fa-ticket"></i> 需報名</span>`;
              }
            } else {
              applyTagHtml = `<span class="meta-tag tag-walkin"><i class="fa-solid fa-door-open"></i> 不需報名</span>`;
            }

            const compactSessionsHtml = renderCompactSessionsHtml(e, true);

            const regLinkHtml = `
              <a href="../%E5%A0%B1%E5%90%8D%E5%88%86%E6%9E%90/index.html?search=${encodeURIComponent(e.title)}" target="_blank" onclick="event.stopPropagation()" class="card-link-reg" title="查看「${e.title}」各場次錄取率分析">
                <i class="fa-solid fa-chart-column"></i> 報名詳情 <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:9.5px;"></i>
              </a>
            `;

            return `
              <div class="building-event-item" id="popup_event_${e.event_id}" onclick="focusEventCard('${e.event_id}')" style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 10px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.03); cursor: pointer; transition: all 0.2s ease;">
                <div class="building-event-item-title" style="font-size: 13.5px; font-weight: 800; color: #0f172a; line-height: 1.35;">${e.title}</div>
                <div class="building-event-item-meta" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 4px 8px; font-size: 11px; margin: 4px 0 6px 0;">
                  <span style="color: #475569; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; line-height: 1.3;">
                    <i class="fa-solid fa-building-columns" style="color: #94a3b8; font-size: 10px;"></i> ${e.organizer || '中研院'}
                  </span>
                  <div style="margin-left: auto; display: flex; align-items: center;">
                    ${applyTagHtml}
                  </div>
                </div>
                ${compactSessionsHtml}
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; padding-top: 4px; border-top: 1px solid #f1f5f9;">
                  ${regLinkHtml}
                  <a href="${e.url}" target="_blank" onclick="event.stopPropagation()" style="color: #2563eb; font-weight: 800; font-size: 11.5px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                    官方詳情 <i class="fa-solid fa-arrow-up-right-from-square"></i>
                  </a>
                </div>
              </div>
            `;
          }).join('');

          marker.bindPopup(`
            <div class="popup-box">
              <div class="popup-title">📍 ${bData.locationName}</div>
              <div class="popup-badge" style="background:#dbeafe; color:#1e40af;">共 ${count} 場開放日活動</div>
              <div class="building-event-list">
                ${eventItemsHtml}
              </div>
            </div>
          `);

          marker.addTo(layerGroupMap['events']);
        });

        if (matchedEvents.length === 0) {
          cardsContainer.innerHTML = `
            <div style="text-align:center; padding: 40px 16px; color: #94a3b8;">
              <i class="fa-solid fa-calendar-xmark" style="font-size: 36px; margin-bottom: 10px; color: #cbd5e1;"></i>
              <div style="font-size: 14px; font-weight: 700; color: #475569;">無符合條件的活動</div>
              <div style="font-size: 12px; margin-top: 4px; color: #94a3b8;">請嘗試調整時間區間、關鍵字或篩選條件</div>
            </div>
          `;
        }

        matchedEvents.forEach(ev => {
          const card = document.createElement('div');
          card.className = 'event-card';
          card.id = `card_${ev.event_id}`;

          let themeClass = 'theme-kids';
          if ((ev.theme || '').includes('院區')) themeClass = 'theme-open';
          if ((ev.theme || '').includes('南')) themeClass = 'theme-south';

          const regInfo = ev.regInfo || { status: 'walk_in', hasStats: false };

          let applyTagHtml = '';
          if (ev.need_apply === '需報名') {
            if (regInfo.hasStats && regInfo.totalLimit > 0) {
              const statClass = regInfo.isOverbooked ? 'overbooked' : 'available';
              applyTagHtml = `<span class="meta-tag tag-reg-stat ${statClass}" title="全場累計已報名 ${regInfo.totalWait} 人 / 總限額 ${regInfo.totalLimit} 人"><i class="fa-solid fa-users"></i> 報名 <b>${regInfo.totalWait}</b> / 名額 <b>${regInfo.totalLimit}</b></span>`;
            } else {
              applyTagHtml = `<span class="meta-tag tag-needapply"><i class="fa-solid fa-ticket"></i> 需報名</span>`;
            }
          } else {
            applyTagHtml = `<span class="meta-tag tag-walkin"><i class="fa-solid fa-door-open"></i> 不需報名</span>`;
          }

          const compactSessionsHtml = renderCompactSessionsHtml(ev, false);

          const regLinkHtml = `
            <a href="../%E5%A0%B1%E5%90%8D%E5%88%86%E6%9E%90/index.html?search=${encodeURIComponent(ev.title)}" target="_blank" class="card-link-reg" onclick="event.stopPropagation()" title="查看此活動各場次報名人數與錄取率">
              <i class="fa-solid fa-chart-column"></i> 報名詳情 <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:9.5px;"></i>
            </a>
          `;

          card.innerHTML = `
            <div class="card-top">
              <div class="card-title">${ev.title}</div>
              <div class="theme-pill ${themeClass}">${ev.theme || '一般活動'}</div>
            </div>
            <div class="card-organizer">
              <i class="fa-solid fa-building-columns"></i> ${ev.organizer}
            </div>
            <div class="card-meta-tags">
              <span class="meta-tag"><i class="fa-solid fa-tags"></i> ${ev.event_type || '活動'}</span>
              ${applyTagHtml}
              <span class="meta-tag"><i class="fa-solid fa-users"></i> ${ev.target || '全年齡'}</span>
            </div>
            <div class="card-location">
              <span><i class="fa-solid fa-location-dot" style="color:#dc2626;"></i> ${ev.location || '活動地點'}</span>
              <a href="https://maps.google.com?q=${ev.lat},${ev.lng}" target="_blank" onclick="event.stopPropagation()" style="color:#2563eb; font-size:11px; font-weight:800; text-decoration:none;">
                Google導航 <i class="fa-solid fa-diamond-turn-right"></i>
              </a>
            </div>
            ${compactSessionsHtml}
            <div class="card-footer">
              <span style="font-size:11px; color:#64748b;">場次: ${ev.sessions ? ev.sessions.length : 1} 場</span>
              <div class="card-footer-actions">
                ${regLinkHtml}
                <a href="${ev.url}" target="_blank" class="card-link" onclick="event.stopPropagation()">
                  官方詳情 <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
              </div>
            </div>
          `;

          card.onclick = () => {
            document.querySelectorAll('.event-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            if (ev.lat && ev.lng) {
              const lat = parseFloat(ev.lat);
              const lng = parseFloat(ev.lng);
              const key = `${lat.toFixed(4)},${lng.toFixed(4)}`;
              const marker = buildingMarkersMap.get(key);

              map.flyTo([lat, lng], 18, { duration: 0.8 });

              if (marker) {
                setTimeout(() => {
                  marker.openPopup();
                  const popupItem = document.getElementById(`popup_event_${ev.event_id}`);
                  if (popupItem) {
                    document.querySelectorAll('.building-event-item').forEach(el => {
                      el.style.borderColor = '#e2e8f0';
                      el.style.background = '#ffffff';
                    });
                    popupItem.style.borderColor = '#2563eb';
                    popupItem.style.background = '#eff6ff';
                    popupItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                  }
                }, 250);
              }
              if (window.innerWidth <= 768) closeMobileDrawer();
            }
          };

          cardsContainer.appendChild(card);
        });
      } else {
        if (layerGroupMap['events'] && map.hasLayer(layerGroupMap['events'])) {
          map.removeLayer(layerGroupMap['events']);
        }
      }

      allFacilitiesData.forEach(fac => {
        if (activeLayers.has(fac.category)) {
          if (currentThemeFilter === '南部院區開放日') {
            if (fac.lat >= 24.0) return;
          } else if (currentThemeFilter === '兒童科普日' || currentThemeFilter === '院區開放日') {
            if (fac.lat < 24.0) return;
          }

          if (layerGroupMap[fac.category] && !map.hasLayer(layerGroupMap[fac.category])) {
            layerGroupMap[fac.category].addTo(map);
          }
          const pin = createFacilityPin(fac.category);
          const fMarker = L.marker([fac.lat, fac.lng], { icon: pin });
          
          fMarker.bindPopup(`
            <div class="popup-box">
              <div class="popup-title">📍 ${fac.name}</div>
              <div class="popup-badge fac-${fac.category}" style="color:#ffffff; font-weight:800;">${fac.category}</div>
              ${fac.description ? `<div class="popup-desc">${fac.description}</div>` : ''}
              <div style="margin-top:6px;">
                <a href="https://maps.google.com?q=${fac.lat},${fac.lng}" target="_blank" style="color:#2563eb; font-weight:800; font-size:11.5px; text-decoration:none;">
                  Google導航 <i class="fa-solid fa-diamond-turn-right"></i>
                </a>
              </div>
            </div>
          `);

          fMarker.addTo(layerGroupMap[fac.category]);

          if (!activeLayers.has('events')) {
            const fCard = document.createElement('div');
            fCard.className = `facility-card fac-${fac.category}`;
            fCard.innerHTML = `
              <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                <div style="font-weight:800; font-size:14px; color:#0f172a; line-height:1.35;">📍 ${fac.name}</div>
                <span class="popup-badge fac-${fac.category}" style="color:#ffffff; font-size:10.5px; font-weight:800; padding:2px 8px; border-radius:5px; flex-shrink:0;">${fac.category}</span>
              </div>
              ${fac.description ? `<div style="font-size:12px; color:#475569; line-height:1.5; white-space:pre-line; margin-top:2px;">${fac.description}</div>` : ''}
              <div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px; padding-top:6px; border-top:1px solid #f1f5f9;">
                <span style="font-size:11px; color:#94a3b8;"><i class="fa-solid fa-map-pin"></i> ${fac.folder_name || '週邊設施'}</span>
                <a href="https://maps.google.com?q=${fac.lat},${fac.lng}" target="_blank" onclick="event.stopPropagation()" style="color:#2563eb; font-size:11.5px; font-weight:800; text-decoration:none; display:inline-flex; align-items:center; gap:4px;">
                  Google 導航 <i class="fa-solid fa-diamond-turn-right"></i>
                </a>
              </div>
            `;
            fCard.onclick = () => {
              map.flyTo([fac.lat, fac.lng], 18, { duration: 0.8 });
              fMarker.openPopup();
              if (window.innerWidth <= 768) closeMobileDrawer();
            };
            cardsContainer.appendChild(fCard);
          }
        } else {
          if (layerGroupMap[fac.category] && map.hasLayer(layerGroupMap[fac.category])) {
            map.removeLayer(layerGroupMap[fac.category]);
          }
        }
      });
    }

    function toggleLayer(layerName, el) {
      if (layerName === 'events') {
        if (activeLayers.has('events')) {
          activeLayers.delete('events');
          el.classList.remove('active');
        } else {
          activeLayers.add('events');
          el.classList.add('active');
        }
      } else {
        if (activeLayers.has(layerName)) {
          activeLayers.delete(layerName);
          el.classList.remove('active');
          if (layerGroupMap[layerName] && map.hasLayer(layerGroupMap[layerName])) {
            map.removeLayer(layerGroupMap[layerName]);
          }
        } else {
          activeLayers.add(layerName);
          el.classList.add('active');
          if (layerGroupMap[layerName] && !map.hasLayer(layerGroupMap[layerName])) {
            layerGroupMap[layerName].addTo(map);
          }

          const isSouth = (currentThemeFilter === '南部院區開放日') || (currentThemeFilter === 'ALL' && map.getCenter().lat < 24.0);
          const facs = allFacilitiesData.filter(f => f.category === layerName && (isSouth ? f.lat < 24.0 : f.lat > 24.0));
          if (facs.length > 0) {
            const first = facs[0];
            map.flyTo([first.lat, first.lng], 17, { duration: 0.8 });
          }
        }
      }
      applyFilters();
    }

    function updateThemeChipActive(theme) {
      document.querySelectorAll('.theme-card-chip').forEach(c => {
        if (c.getAttribute('data-theme') === theme) {
          c.classList.add('active');
        } else {
          c.classList.remove('active');
        }
      });
    }

    function setThemeFilter(theme, el) {
      currentThemeFilter = theme;
      if (theme !== '南部院區開放日') {
        lastNankangTheme = theme;
      }
      if (el) {
        document.querySelectorAll('.theme-card-chip').forEach(c => c.classList.remove('active'));
        el.classList.add('active');
      } else {
        updateThemeChipActive(theme);
      }

      if (theme === '南部院區開放日') {
        flyToCampus('south', false);
      } else if (theme === '兒童科普日' || theme === '院區開放日') {
        flyToCampus('nankang', false);
      }

      applyFilters();
    }

    function flyToCampus(campus, syncTheme = true) {
      document.querySelectorAll('.campus-btn').forEach(b => b.classList.remove('active'));
      if (campus === 'nankang') {
        const btn = document.getElementById('btnCampusNankang');
        if (btn) btn.classList.add('active');
        map.flyTo([25.0418, 121.6145], 16, { duration: 0.8 });

        if (syncTheme) {
          if (currentThemeFilter === '南部院區開放日') {
            currentThemeFilter = lastNankangTheme || 'ALL';
            updateThemeChipActive(currentThemeFilter);
            applyFilters();
          }
        }
      } else if (campus === 'south') {
        const btn = document.getElementById('btnCampusSouth');
        if (btn) btn.classList.add('active');
        map.flyTo([22.9245, 120.2919], 16, { duration: 0.8 });

        if (syncTheme) {
          if (currentThemeFilter !== '南部院區開放日') {
            currentThemeFilter = '南部院區開放日';
            updateThemeChipActive('南部院區開放日');
            applyFilters();
          }
        }
      }
    }

    function focusEventCard(eventId) {
      const card = document.getElementById(`card_${eventId}`);
      if (card) {
        document.querySelectorAll('.event-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    function openMobileDrawer() {
      const panel = document.getElementById('sidebarPanel');
      const backdrop = document.getElementById('mobileBackdrop');
      if (panel) panel.classList.add('open');
      if (backdrop) backdrop.classList.add('active');
    }

    function closeMobileDrawer() {
      const panel = document.getElementById('sidebarPanel');
      const backdrop = document.getElementById('mobileBackdrop');
      if (panel) panel.classList.remove('open');
      if (backdrop) backdrop.classList.remove('active');
    }

    applyFilters();
  </script>
</body>
</html>
"""

    html_content = html_template.replace('__EVENTS_JSON__', json.dumps(events, ensure_ascii=False))
    html_content = html_content.replace('__FACILITIES_JSON__', json.dumps(facs, ensure_ascii=False))
    html_content = html_content.replace('__REGISTRATION_JSON__', json.dumps(regs, ensure_ascii=False))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("index.html successfully updated with compact, beautiful RWD layout!")

if __name__ == '__main__':
    build()

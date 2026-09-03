# 院區開放 這些年 — Demo

中央研究院院區開放活動輯（2022–2025）的**捲動敘事（scrollytelling）技術 Demo**。
純靜態網頁，無後端；`MAP/` 為互動地圖子頁。

> ⚠️ **本站為 Demo 測試，非中央研究院官方網站。** 內容與圖片僅供技術展示。

## 技術

HTML / CSS / JS · GSAP + ScrollTrigger · Lenis（`?smooth` 開啟）· Leaflet（地圖）

## 本機預覽

```bash
python -m http.server 8123
# 開 http://127.0.0.1:8123/
```

## 部署（GitHub Pages）

1. 建立 Public repo，把**本資料夾內容**推上去（不要含上層的內部文件）
2. Settings → Pages → Branch: `main` /（root）→ Save
3. 約 1–2 分鐘後：`https://<帳號>.github.io/<repo>/`（地圖在 `/MAP/`）

@app.get("/mypage.html")
async def read_mypage(request: Request):
    return templates.TemplateResponse("mypage.html", {"request": request})
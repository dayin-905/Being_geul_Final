
# Final Bug Fixes & System Documentation

## 1. System Documentation (Mermaid)

### 1-1. System Architecture
- **File**: `system_architecture.md`
- **Content**: Visualized the Client-Server-DB architecture using Mermaid diagram. Included detailed descriptions of Frontend (HTML/JS/Tailwind), Backend (FastAPI), and Database (PostgreSQL).
- **Fix**: Corrected Mermaid syntax error where node labels with parentheses e.g., `(auth.py)` were causing parsing failures. Added double quotes around strings.

### 1-2. ERD (Entity Relationship Diagram)
- **File**: `database_erd.md`
- **Content**: Visualized the database schema including `users`, `being_test` (policies), and `users_action` tables using Mermaid ER diagram.

### 1-3. System Use Case
- **File**: `usecase_diagram.md`
- **Content**: Defined actor interactions (Guest, User, Admin) with system features like Policy Discovery, My Page, and Admin Management.

---

## 2. Bug Fixes

### 2-1. About Page Video Fix
- **Issue**: The YouTube video on `about.html` was displaying an "Unavailable" error.
- **Cause**: The video ID in the `playlist` parameter did not match the new video logic.
- **Fix**: Updated the `src` URL in `templates/about.html` to sync the video ID and playlist ID for seamless looping.
  ```html
  src="https://www.youtube.com/embed/0cBFceNkvfY?autoplay=1&mute=1&controls=0&loop=1&playlist=0cBFceNkvfY"
  ```

### 2-2. 500 Internal Server Error (Main Page & All Page)
- **Issue**: `500 Internal Server Error` occurred when accessing `main.html` or `all.html` with certain parameters.
- **Cause**: The helper function `get_image_for_category` raised a `TypeError` when a policy's genre (category) was `None` (NULL).
- **Fix 1 (models.py)**: Added a safety check to convert `None` to an empty string.
  ```python
  def get_image_for_category(category: str) -> str:
      if not category:  # Handle None
          category = ""
      # ... existing logic ...
  ```
- **Fix 2 (routers/all.py)**: Removed the duplicate, faulty `get_image_for_category` function inside `routers/all.py` and imported the corrected version from `models.py` to ensure consistency.

### 2-3. Favicon 404 Error
- **Issue**: Browser console showed `GET /favicon.ico 404 (Not Found)`.
- **Cause**: The browser automatically requests `favicon.ico`, but the file does not exist in the project root or static folder.
- **Note**: This is a minor warning and does not affect functionality. To fix, simply add a `favicon.ico` file to the static directory.

---

## 3. Summary of Files Modified
| File Path | Description |
|-----------|-------------|
| `templates/about.html` | Updated YouTube video URL. |
| `models.py` | Fixed `get_image_for_category` to handle `None` values. |
| `routers/all.py` | Removed duplicate function and imported from `models.py`. |
| `system_architecture.md` | Created and fixed Mermaid syntax. |
| `database_erd.md` | Created ERD documentation. |
| `usecase_diagram.md` | Created Use Case documentation. |

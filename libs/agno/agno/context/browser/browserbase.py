"""BrowserbaseBackend — cloud browser automation via Browserbase.

Browserbase provides managed cloud browsers with built-in features like
ad blocking, CAPTCHA solving, and session recording. Use this backend
when you need cloud-hosted browsers instead of local Playwright.

Requires:
    pip install browserbase playwright
    BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables
"""

from __future__ import annotations

from typing import Any

from agno.context.backend import ContextBackend
from agno.context.provider import Status


class BrowserbaseBackend(ContextBackend):
    """Backend for `BrowserContextProvider` using Browserbase cloud browsers."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        project_id: str | None = None,
        block_ads: bool = False,
        solve_captchas: bool = False,
        parse_html: bool = True,
        max_content_length: int | None = 100000,
    ) -> None:
        self.api_key = api_key
        self.project_id = project_id
        self.block_ads = block_ads
        self.solve_captchas = solve_captchas
        self.parse_html = parse_html
        self.max_content_length = max_content_length
        self._tools: Any = None

    def status(self) -> Status:
        features = []
        if self.block_ads:
            features.append("ads-blocked")
        if self.solve_captchas:
            features.append("captcha-solver")
        feature_str = f", {', '.join(features)}" if features else ""
        return Status(ok=True, detail=f"browserbase (cloud{feature_str})")

    async def astatus(self) -> Status:
        return self.status()

    def get_tools(self) -> list:
        if self._tools is None:
            self._tools = self._build_tools()
        return [self._tools]

    def _build_tools(self) -> Any:
        from agno.tools.browserbase import BrowserbaseTools

        return BrowserbaseTools(
            api_key=self.api_key,
            project_id=self.project_id,
            block_ads=self.block_ads,
            solve_captchas=self.solve_captchas,
            parse_html=self.parse_html,
            max_content_length=self.max_content_length,
            all=True,
        )

    async def asetup(self) -> None:
        if self._tools is None:
            self._tools = self._build_tools()

    async def aclose(self) -> None:
        if self._tools is not None:
            try:
                await self._tools.aclose_session()
            except Exception:
                pass
        self._tools = None

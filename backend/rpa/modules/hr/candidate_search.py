"""
BOSS直聘候选人搜索模块
"""

from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from rpa.core.base import BaseModule

logger = get_logger("candidate_search")


class CandidateSearchModule(BaseModule):
    """候选人搜索模块"""

    def __init__(self):
        super().__init__()
        self.base_url = settings.BOSS_URL

    def execute(
        self,
        keyword: str,
        city: str = "全国",
        experience: Optional[str] = None,
        education: Optional[str] = None,
        salary: Optional[str] = None,
        age: Optional[str] = None,
        gender: Optional[str] = None,
        max_pages: int = 1,
        hr_account_id: Optional[int] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        执行候选人搜索

        Args:
            keyword: 职位关键词
            city: 城市
            experience: 工作经验要求
            education: 学历要求
            salary: 期望薪资
            age: 年龄范围
            gender: 性别
            max_pages: 最大搜索页数
            hr_account_id: HR账户ID
            **kwargs: 其他参数

        Returns:
            搜索结果字典
        """
        try:
            # 确保浏览器已初始化
            if not self.browser.is_initialized:
                self.init_browser(**kwargs)

            page = self.browser.get_page()
            candidates = []

            # 构建搜索URL
            search_url = self._build_search_url(keyword, city, experience, education, salary, age, gender)
            self.logger.info(f"Searching candidates: {search_url}")

            # 遍历多页
            for page_num in range(1, max_pages + 1):
                # 访问搜索页面
                url = f"{search_url}&page={page_num}" if page_num > 1 else search_url
                page.get(url, retry=2, timeout=15)
                self.wait(1.5)

                # 解析候选人列表
                page_candidates = self._parse_candidate_list(page)
                if not page_candidates:
                    self.logger.warning(f"No more candidates found on page {page_num}")
                    break

                candidates.extend(page_candidates)
                self.logger.info(f"Found {len(page_candidates)} candidates on page {page_num}")

            self.logger.info(f"Total candidates found: {len(candidates)}")
            return {
                "success": True,
                "data": candidates,
                "total": len(candidates),
                "message": f"成功获取{len(candidates)}个候选人",
                "hr_account_id": hr_account_id,
            }

        except Exception as e:
            self.logger.error(f"Candidate search failed: {e}")
            self.save_screenshot()
            return {
                "success": False,
                "data": [],
                "message": f"搜索失败: {str(e)}",
                "hr_account_id": hr_account_id,
            }

    def _build_search_url(
        self,
        keyword: str,
        city: str,
        experience: Optional[str],
        education: Optional[str],
        salary: Optional[str],
        age: Optional[str],
        gender: Optional[str],
    ) -> str:
        """
        构建候选人搜索URL

        Args:
            keyword: 关键词
            city: 城市
            experience: 经验
            education: 学历
            salary: 薪资
            age: 年龄
            gender: 性别

        Returns:
            搜索URL
        """
        # HR 候选人搜索入口
        url = f"{self.base_url}/web/boss/recommend"

        # 添加查询参数
        params = []
        if keyword:
            params.append(f"query={keyword}")
        if city and city != "全国":
            params.append(f"city={city}")
        if experience:
            params.append(f"experience={experience}")
        if education:
            params.append(f"education={education}")
        if salary:
            params.append(f"salary={salary}")
        if age:
            params.append(f"age={age}")
        if gender:
            params.append(f"gender={gender}")

        if params:
            url += "?" + "&".join(params)

        return url

    def _parse_candidate_list(self, page) -> list[dict[str, Any]]:
        """
        解析候选人列表

        Args:
            page: 浏览器页面对象

        Returns:
            候选人列表
        """
        candidates = []
        try:
            # 查找候选人卡片元素
            # BOSS直聘HR端的候选人卡片选择器
            candidate_elements = page.eles("css:.recommend-card-wrapper", timeout=10)

            if not candidate_elements:
                # 尝试其他可能的选择器
                candidate_elements = page.eles("css:.geek-card", timeout=5)

            self.logger.info(f"Found {len(candidate_elements)} candidate elements")

            for candidate_ele in candidate_elements:
                try:
                    candidate_info = self._parse_candidate_item(candidate_ele)
                    if candidate_info:
                        candidates.append(candidate_info)
                except Exception as e:
                    self.logger.warning(f"Error parsing candidate item: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing candidate list: {e}")

        return candidates

    def _parse_candidate_item(self, candidate_ele) -> Optional[dict[str, Any]]:
        """
        解析单个候选人信息

        Args:
            candidate_ele: 候选人元素

        Returns:
            候选人信息字典
        """
        try:
            # 姓名
            name_ele = candidate_ele.ele("css:.geek-name", timeout=1)
            name = name_ele.text.strip() if name_ele else ""

            # 当前职位
            position_ele = candidate_ele.ele("css:.geek-job", timeout=1)
            position = position_ele.text if position_ele else ""

            # 工作经验
            experience_ele = candidate_ele.ele("css:.geek-experience, .experience-info", timeout=1)
            experience = experience_ele.text if experience_ele else ""

            # 学历
            education_ele = candidate_ele.ele("css:.geek-degree, .degree-info", timeout=1)
            education = education_ele.text if education_ele else ""

            # 期望薪资
            salary_ele = candidate_ele.ele("css:.geek-salary, .salary-info", timeout=1)
            expected_salary = salary_ele.text if salary_ele else ""

            # 最近公司
            company_ele = candidate_ele.ele("css:.geek-company, .company-info", timeout=1)
            recent_company = company_ele.text if company_ele else ""

            # 技能标签
            skills = []
            skill_eles = candidate_ele.eles("css:.geek-skills .skill-tag, .tag-item", timeout=1)
            for skill_ele in skill_eles:
                skill_text = skill_ele.text.strip()
                if skill_text:
                    skills.append(skill_text)

            # 候选人主页链接
            link_ele = candidate_ele.ele("css:.geek-card, a[href*='/geek/']", timeout=1)
            profile_url = ""
            if link_ele:
                href = link_ele.attr("href")
                if href:
                    profile_url = href if href.startswith("http") else self.base_url + href

            # 状态 (是否在线、最近活跃等)
            status_ele = candidate_ele.ele("css:.geek-status, .status-text", timeout=1)
            status = status_ele.text if status_ele else "active"

            return {
                "name": name,
                "position": position,
                "experience": experience,
                "education": education,
                "expected_salary": expected_salary,
                "recent_company": recent_company,
                "skills": ", ".join(skills) if skills else "",
                "profile_url": profile_url,
                "status": status,
            }

        except Exception as e:
            self.logger.warning(f"Error parsing candidate item: {e}")
            return None

    def get_candidate_detail(self, profile_url: str, **kwargs) -> dict[str, Any]:
        """
        获取候选人详情

        Args:
            profile_url: 候选人主页链接
            **kwargs: 其他参数

        Returns:
            候选人详情
        """
        try:
            if not self.browser.is_initialized:
                self.init_browser(**kwargs)

            page = self.browser.get_page()

            # 访问候选人主页
            if not profile_url.startswith("http"):
                profile_url = self.base_url + profile_url

            page.get(profile_url, retry=2, timeout=15)
            self.wait(1)

            # 解析详情页
            detail = self._parse_candidate_detail(page)

            return {"success": True, "data": detail}

        except Exception as e:
            self.logger.error(f"Failed to get candidate detail: {e}")
            return {"success": False, "message": str(e)}

    def _parse_candidate_detail(self, page) -> dict[str, Any]:
        """
        解析候选人详情

        Args:
            page: 浏览器页面对象

        Returns:
            候选人详情
        """
        try:
            # 获取更多信息...
            # 联系方式、工作经历、教育背景等

            # 工作经历
            experiences = []
            exp_eles = page.eles("css:.work-experience-item", timeout=5)
            for exp_ele in exp_eles:
                exp = {
                    "company": exp_ele.ele("css:.exp-company").text if exp_ele.ele("css:.exp-company") else "",
                    "position": exp_ele.ele("css:.exp-position").text if exp_ele.ele("css:.exp-position") else "",
                    "duration": exp_ele.ele("css:.exp-duration").text if exp_ele.ele("css:.exp-duration") else "",
                }
                experiences.append(exp)

            # 教育背景
            educations = []
            edu_eles = page.eles("css:.education-item", timeout=5)
            for edu_ele in edu_eles:
                edu = {
                    "school": edu_ele.ele("css:.edu-school").text if edu_ele.ele("css:.edu-school") else "",
                    "major": edu_ele.ele("css:.edu-major").text if edu_ele.ele("css:.edu-major") else "",
                    "degree": edu_ele.ele("css:.edu-degree").text if edu_ele.ele("css:.edu-degree") else "",
                }
                educations.append(edu)

            return {
                "experiences": experiences,
                "educations": educations,
            }

        except Exception as e:
            self.logger.error(f"Error parsing candidate detail: {e}")
            return {}

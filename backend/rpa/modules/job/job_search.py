"""
BOSS直聘职位搜索模块
"""

from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from rpa.core.base import BaseModule

logger = get_logger("job_search")


class JobSearchModule(BaseModule):
    """职位搜索模块"""

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
        max_pages: int = 1,
        **kwargs,
    ) -> dict[str, Any]:
        """
        执行职位搜索

        Args:
            keyword: 搜索关键词
            city: 城市
            experience: 工作经验
            education: 学历要求
            salary: 薪资范围
            max_pages: 最大搜索页数
            **kwargs: 其他参数

        Returns:
            搜索结果字典
        """
        try:
            # 确保浏览器已初始化
            if not self.browser.is_initialized:
                self.init_browser(**kwargs)

            page = self.browser.get_page()
            jobs = []

            # 构建搜索URL
            search_url = self._build_search_url(keyword, city, experience, education, salary)
            self.logger.info(f"Searching jobs: {search_url}")

            # 遍历多页
            for page_num in range(1, max_pages + 1):
                # 访问搜索页面
                url = f"{search_url}&page={page_num}" if page_num > 1 else search_url
                page.get(url, retry=2, timeout=15)
                self.wait(1.5)

                # 解析职位列表
                page_jobs = self._parse_job_list(page)
                if not page_jobs:
                    self.logger.warning(f"No more jobs found on page {page_num}")
                    break

                jobs.extend(page_jobs)
                self.logger.info(f"Found {len(page_jobs)} jobs on page {page_num}")

            self.logger.info(f"Total jobs found: {len(jobs)}")
            return {
                "success": True,
                "data": jobs,
                "total": len(jobs),
                "message": f"成功获取{len(jobs)}个职位",
            }

        except Exception as e:
            self.logger.error(f"Job search failed: {e}")
            self.save_screenshot()
            return {
                "success": False,
                "data": [],
                "message": f"搜索失败: {str(e)}",
            }

    def _build_search_url(
        self,
        keyword: str,
        city: str,
        experience: Optional[str],
        education: Optional[str],
        salary: Optional[str],
    ) -> str:
        """
        构建搜索URL

        Args:
            keyword: 关键词
            city: 城市
            experience: 经验
            education: 学历
            salary: 薪资

        Returns:
            搜索URL
        """
        # 基础URL
        url = f"{self.base_url}/web/geek/job"

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

        if params:
            url += "?" + "&".join(params)

        return url

    def _parse_job_list(self, page) -> list[dict[str, Any]]:
        """
        解析职位列表

        Args:
            page: 浏览器页面对象

        Returns:
            职位列表
        """
        jobs = []
        try:
            # 查找职位列表元素
            job_elements = page.eles("css:.job-card-wrapper", timeout=10)

            self.logger.info(f"Found {len(job_elements)} job elements")

            for job_ele in job_elements:
                try:
                    job_info = self._parse_job_item(job_ele)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    self.logger.warning(f"Error parsing job item: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing job list: {e}")

        return jobs

    def _parse_job_item(self, job_ele) -> Optional[dict[str, Any]]:
        """
        解析单个职位信息

        Args:
            job_ele: 职位元素

        Returns:
            职位信息字典
        """
        try:
            # 职位名称
            job_name_ele = job_ele.ele("css:.job-title", timeout=1)
            job_name = job_name_ele.text if job_name_ele else ""

            # 薪资
            salary_ele = job_ele.ele("css:.salary", timeout=1)
            salary = salary_ele.text if salary_ele else ""

            # 公司信息
            company_ele = job_ele.ele("css:.company-name a", timeout=1)
            company_name = company_ele.text if company_ele else ""

            # 职位链接
            link_ele = job_ele.ele("css:.job-card-left", timeout=1)
            job_url = link_ele.attr("href") if link_ele else ""
            if job_url and not job_url.startswith("http"):
                job_url = self.base_url + job_url

            # 区域
            area_ele = job_ele.ele("css:.job-area", timeout=1)
            area = area_ele.text if area_ele else ""

            # 标签 (经验、学历等)
            tags = []
            tag_eles = job_ele.eles("css:.job-info .tag-list li", timeout=1)
            for tag_ele in tag_eles:
                tag_text = tag_ele.text
                if tag_text:
                    tags.append(tag_text)

            # 解析经验和学历
            experience = tags[0] if len(tags) > 0 else None
            education = tags[1] if len(tags) > 1 else None

            # 行业和公司规模
            industry_ele = job_ele.ele("css:.job-info .company-tag-list", timeout=1)
            industry = industry_ele.text if industry_ele else ""

            # BOSS信息
            boss_ele = job_ele.ele("css:.boss-info", timeout=1)
            boss_title = boss_ele.text if boss_ele else ""

            return {
                "job_name": job_name,
                "salary": salary,
                "company_name": company_name,
                "job_url": job_url,
                "area": area,
                "city": area.split("·")[0] if "·" in area else area,
                "experience": experience,
                "education": education,
                "industry": industry,
                "boss_title": boss_title,
            }

        except Exception as e:
            self.logger.warning(f"Error parsing job item: {e}")
            return None

    def get_job_detail(self, job_url: str, **kwargs) -> dict[str, Any]:
        """
        获取职位详情

        Args:
            job_url: 职位链接
            **kwargs: 其他参数

        Returns:
            职位详情
        """
        try:
            if not self.browser.is_initialized:
                self.init_browser(**kwargs)

            page = self.browser.get_page()

            # 访问职位详情页
            if not job_url.startswith("http"):
                job_url = self.base_url + job_url

            page.get(job_url, retry=2, timeout=15)
            self.wait(1)

            # 解析详情页
            detail = self._parse_job_detail(page)

            return {"success": True, "data": detail}

        except Exception as e:
            self.logger.error(f"Failed to get job detail: {e}")
            return {"success": False, "message": str(e)}

    def _parse_job_detail(self, page) -> dict[str, Any]:
        """
        解析职位详情

        Args:
            page: 浏览器页面对象

        Returns:
            职位详情
        """
        try:
            # 职位描述
            jd_ele = page.ele("css:.job-sec-text", timeout=5)
            job_description = jd_ele.text if jd_ele else ""

            # 公司地址
            address_ele = page.ele("css:.job-location .location-address", timeout=5)
            address = address_ele.text if address_ele else ""

            return {
                "job_description": job_description,
                "address": address,
            }

        except Exception as e:
            self.logger.error(f"Error parsing job detail: {e}")
            return {}

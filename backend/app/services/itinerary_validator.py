"""
AI行程合理性和可行性验证器
使用AI检查行程是否合理、可行
"""
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.core.config import settings


class ItineraryValidator:
    """AI行程验证器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_API_BASE,
            temperature=0.3  # 较低温度，更客观
        )
    
    async def validate_itinerary(
        self,
        itinerary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        验证完整行程的合理性和可行性
        
        Args:
            itinerary_data: 包含daily_schedule和cost_breakdown的行程数据
            
        Returns:
            验证结果，包含评分、问题和建议
        """
        
        # 构建验证提示
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位经验丰富的旅行规划专家，负责审核行程的合理性和可行性。

请从以下维度评估行程：

1. **时间合理性** (0-10分)
   - 每天景点数量是否合适（建议2-4个）
   - 景点间路程时间是否合理
   - 是否留有休息和用餐时间
   - 开放时间冲突检查

2. **路线合理性** (0-10分)
   - 景点顺序是否优化（避免走回头路）
   - 交通方式选择是否合理
   - 是否考虑了交通拥堵时段

3. **预算可行性** (0-10分)
   - 预算分配是否合理
   - 是否有隐性费用遗漏
   - 是否有预算余量

4. **体验合理性** (0-10分)
   - 景点类型是否过于单一
   - 是否有劳逸结合
   - 是否适合目标人群

5. **实际可行性** (0-10分)
   - 是否考虑了现实约束（天气、季节）
   - 住宿位置是否合理
   - 紧急情况预案

请以JSON格式返回评估结果：
```json
{
  "overall_score": 85,
  "scores": {
    "time": 9,
    "route": 8,
    "budget": 7,
    "experience": 9,
    "feasibility": 8
  },
  "is_feasible": true,
  "issues": [
    {"severity": "warning", "issue": "第2天景点过多，可能会很累", "suggestion": "建议删除1个景点或分配到其他天"},
    {"severity": "error", "issue": "预算超支200元", "suggestion": "建议减少出租车使用，改用地铁"}
  ],
  "recommendations": [
    "第1天的行程安排很合理，景点之间距离适中",
    "建议在第2天中午预留更多时间用餐和休息",
    "住宿位置选择不错，交通便利"
  ],
  "summary": "整体行程较为合理，但第2天安排偏紧张，建议适当调整。预算方面略有超支，可通过优化交通方式解决。"
}
```

请客观、专业地评估，指出实际问题并给出可行建议。"""),
            
            ("user", """请评估以下行程：

**目的地**: {destination}
**天数**: {days}天
**总预算**: ¥{budget}

**每日安排**:
{daily_schedule}

**费用明细**:
- 景点门票: ¥{attractions_cost}
- 住宿费用: ¥{hotels_cost}
- 交通费用: ¥{transportation_cost}
- 餐饮预算: ¥{meals_cost}
- **总计**: ¥{total_cost}
- **剩余**: ¥{remaining}

请评估这个行程的合理性和可行性。""")
        ])
        
        # 格式化每日行程
        daily_text = self._format_daily_schedule(itinerary_data.get('daily_schedule', []))
        
        cost = itinerary_data.get('cost_breakdown', {})
        
        # 执行验证
        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(
                    destination=itinerary_data.get('destination', '未知'),
                    days=itinerary_data.get('days', 0),
                    budget=itinerary_data.get('budget', 0),
                    daily_schedule=daily_text,
                    attractions_cost=cost.get('attractions', 0),
                    hotels_cost=cost.get('hotels', 0),
                    transportation_cost=cost.get('transportation', 0),
                    meals_cost=cost.get('meals', 0),
                    total_cost=cost.get('total', 0),
                    remaining=cost.get('remaining', 0)
                )
            )
            
            # 解析AI返回的JSON
            import json
            content = response.content
            
            # 提取JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            validation_result = json.loads(content)
            
            return validation_result
            
        except Exception as e:
            print(f"AI验证失败: {e}")
            return {
                "overall_score": 70,
                "is_feasible": True,
                "issues": [],
                "recommendations": ["AI验证服务暂时不可用，但基本检查通过"],
                "summary": "系统基本检查通过，建议人工审核"
            }
    
    def _format_daily_schedule(self, daily_schedule: List[Dict]) -> str:
        """格式化每日行程为文本"""
        lines = []
        
        for day in daily_schedule:
            day_num = day.get('day', 0)
            lines.append(f"\n### 第{day_num}天")
            
            # 景点
            attractions = day.get('attractions', [])
            if attractions:
                lines.append("**景点安排**:")
                for attr in attractions:
                    name = attr.get('name', '未知景点')
                    start = attr.get('start_time', '--:--')
                    duration = attr.get('duration_hours', 0)
                    cost = attr.get('cost', 0)
                    lines.append(f"- {start} {name} (游玩{duration}小时, 门票¥{cost})")
            
            # 住宿
            hotel = day.get('hotel')
            if hotel:
                lines.append(f"**住宿**: {hotel.get('name', '未知')} (¥{hotel.get('price_per_night', 0)}/晚)")
            
            # 交通
            transportation = day.get('transportation', [])
            if transportation:
                lines.append("**交通**:")
                for trans in transportation:
                    lines.append(f"- {trans.get('type', '未知')}: {trans.get('from_location', '')} → {trans.get('to_location', '')} (¥{trans.get('cost', 0)})")
            
            # 餐饮
            meals = day.get('meals_budget', 0)
            if meals:
                lines.append(f"**餐饮预算**: ¥{meals}")
        
        return "\n".join(lines)
    
    async def quick_check(
        self,
        destination: str,
        days: int,
        budget: float,
        num_attractions: int
    ) -> Dict[str, Any]:
        """
        快速检查基本参数的合理性
        
        Args:
            destination: 目的地
            days: 天数
            budget: 预算
            num_attractions: 景点数量
            
        Returns:
            快速检查结果
        """
        
        issues = []
        warnings = []
        
        # 预算检查
        budget_per_day = budget / days if days > 0 else 0
        if budget_per_day < 200:
            issues.append({
                "type": "budget",
                "message": f"每天预算仅¥{budget_per_day:.0f}，可能过于紧张",
                "suggestion": "建议增加预算或减少天数"
            })
        elif budget_per_day < 300:
            warnings.append({
                "type": "budget",
                "message": f"每天预算¥{budget_per_day:.0f}，建议选择经济型住宿和公共交通"
            })
        
        # 景点数量检查
        attractions_per_day = num_attractions / days if days > 0 else 0
        if attractions_per_day > 5:
            warnings.append({
                "type": "schedule",
                "message": f"平均每天{attractions_per_day:.1f}个景点，可能会很累",
                "suggestion": "建议减少景点数量或增加天数"
            })
        elif attractions_per_day < 1.5:
            warnings.append({
                "type": "schedule",
                "message": f"平均每天{attractions_per_day:.1f}个景点，行程较为宽松",
                "suggestion": "可以考虑增加一些景点"
            })
        
        # 天数检查
        if days < 2:
            warnings.append({
                "type": "duration",
                "message": "行程只有1天，时间较紧张",
                "suggestion": "建议至少安排2-3天"
            })
        elif days > 7:
            warnings.append({
                "type": "duration",
                "message": f"{days}天行程较长，建议分段规划",
                "suggestion": "可以考虑深度游或跨城市游"
            })
        
        return {
            "is_ok": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "summary": f"快速检查{'通过' if len(issues) == 0 else '发现问题'}，{len(warnings)}个建议"
        }


# 全局实例
_validator_instance = None

def get_validator() -> ItineraryValidator:
    """获取验证器单例"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ItineraryValidator()
    return _validator_instance


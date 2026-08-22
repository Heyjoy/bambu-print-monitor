"""Display formatting helpers — pure functions, no dependencies."""

STATE_MAP = {
    'IDLE': '空闲',
    'RUNNING': '打印中',
    'PAUSE': '已暂停',
    'FINISH': '已完成',
    'FAILED': '打印失败',
    'PREPARE': '准备中',
    'unknown': '未知',
}


def state_cn(state: str) -> str:
    """Printer state code -> Chinese label. Unknown states pass through
    unchanged so the raw value stays visible for debugging."""
    return STATE_MAP.get(state, state)


def format_remaining_time(minutes: int) -> str:
    """Remaining minutes -> human-readable string. <=0 returns '--'
    (printer idle, or firmware occasionally reports negative values)."""
    if minutes <= 0:
        return '--'
    hours, mins = divmod(minutes, 60)
    return f'{hours}小时{mins}分钟' if hours else f'{mins}分钟'

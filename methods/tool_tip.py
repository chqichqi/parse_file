import tkinter as tk


# 自定义ToolTip功能
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, tip_txt):
        "Display text in tooltip window"
        self.tip_txt = tip_txt
        if self.tipwindow or not self.tip_txt:
            return
        x, y, _cx, cy = self.widget.bbox('insert')
        x = x + self.widget.winfo_rootx()+10
        y = y + cy + self.widget.winfo_rooty()+10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)   # 1表示视觉上窗体边框消失
        tw.wm_geometry("+%d+%d" % (x, y))
        # 这里设置的背景颜色无效
        label = tk.Label(tw, text=self.tip_txt, justify=tk.LEFT,
                         background='lightyellow', relief=tk.SOLID,
                         borderwidth=1, font=('tahoma', '10', 'normal'))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# create tooltip
def createToolTip(widget, tip_txt):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(tip_txt)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<FocusIn>', enter)  # Enter
    widget.bind('<FocusOut>', leave)   # Leave
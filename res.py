import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

class ColorBar(pg.GraphicsObject):
    def __init__(self, cmap, width, height, ticks=None, tick_labels=None, label=None):
        pg.GraphicsObject.__init__(self)

        # handle args
        label = label or ''
        w, h = width, height
        stops, colors = cmap.getStops('float')
        smn, spp = stops.min(), stops.ptp()
        stops = (stops - stops.min())/stops.ptp()
        if ticks is None:
            ticks = np.r_[0.0:1.0:5j, 1.0] * spp + smn
        tick_labels = tick_labels or ["%0.2g" % (t,) for t in ticks]

        # setup picture
        self.pic = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(self.pic)

        # draw bar with gradient following colormap
        p.setPen(pg.mkPen('k'))
        grad = pg.QtGui.QLinearGradient(w/2.0, 0.0, w/2.0, h*1.0)
        for stop, color in zip(stops, colors):
            grad.setColorAt(1.0 - stop, pg.QtGui.QColor(*[255*c for c in color]))
        p.setBrush(pg.QtGui.QBrush(grad))
        p.drawRect(pg.QtCore.QRectF(0, 0, w, h))

        # draw ticks & tick labels
        mintx = 0.0
        for tick, tick_label in zip(ticks, tick_labels):
            y_ = (1.0 - (tick - smn)/spp) * h
            p.drawLine(0.0, y_, -5.0, y_)
            br = p.boundingRect(0, 0, 0, 0, pg.QtCore.Qt.AlignRight, tick_label)
            if br.x() < mintx:
                mintx = br.x()
            p.drawText(br.x() - 10.0, y_ + br.height() / 4.0, tick_label)
        # draw label
        br = p.boundingRect(0, 0, 0, 0, pg.QtCore.Qt.AlignRight, label)
        p.drawText(-br.width() / 2.0, h + br.height() + 5.0, label)
        # done
        p.end()
        # compute rect bounds for underlying mask
        self.zone = mintx - 12.0, -15.0, br.width() - mintx, h + br.height() + 30.0

    def paint(self, p, *args):
        # paint underlying mask
        p.setPen(pg.QtGui.QColor(255, 255, 255, 0))
        p.setBrush(pg.QtGui.QColor(255, 255, 255, 200))
        p.drawRoundedRect(*(self.zone + (9.0, 9.0)))
        # paint colorbar
        p.drawPicture(0, 0, self.pic)

    def boundingRect(self):
        return pg.QtCore.QRectF(self.pic.boundingRect())

pg.mkQApp()
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('pyqtgraph example: Image Analysis')
xmin, xmax = -1, 1
ymin, ymax = -1, 1
stops = np.r_[-1.0, -0.5, 0.5, 1.0]
colors = np.array([
    [0, 0, 1, 0.7],
    [0, 1, 0, 0.2],
    [0, 0, 0, 0.8],
    [1, 0, 0, 1.0],
])
cm = pg.ColorMap(stops, colors)
lut = cm.getLookupTable(0.0, 1.0, 256)

cb = ColorBar(cm, 20, 200, label='      %      ')

p1 = win.addPlot()
img = pg.ImageItem(border='k')
p1.addItem(img)
p1.setLabel('left', "Y Axis", units='m')
p1.setLabel('bottom', "X Axis", units='m')
p1.showGrid(x=True, y=True)
# формируем данные для отоборажения
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
data = np.random.normal(size=(200, 100))
data[20:80, 20:80] += 2.
data = pg.gaussianFilter(data, (3, 3))
data += np.random.normal(size=(200, 100)) * 0.1
print('min', np.min(data), 'max', np.max(data))
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
xscale = (xmax-xmin)/data.shape[0]
yscale = (ymax-ymin)/data.shape[1]
img.setImage(data)
img.translate(xmin, ymin)
img.scale(xscale, yscale)
img.setLookupTable(lut)
img.setLevels([stops[0], stops[-1]])

p1.scene().addItem(cb)
cb.translate(120.0, 40.0)
p1.autoRange()
win.show()
# back to drawing cracks
'''
p1.clear()
p1.plot(data[0])
p1.scene().removeItem(cb)
p1.autoRange()
'''
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

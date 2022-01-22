
class Rack(html.CANVAS):
	def __init__(self, u=1):
		html.CANVAS.__init__(self, width="200", height="%d"%(20*u), style={"border":"1px solid #d3d3d3"} )
		ctx = self.getContext("2d")
		self.units = []
	def putUnit(self, pos, h, div):
		self.units.append( Unit(self, pos, h, div) )

class Unit():
	def __init__(self, canvas, pos, h, div=1):
		ctx = canvas.getContext("2d")
		ctx.fillStyle = "#CCCCCC";
		ctx.strokeStyle = "#000000"
		y=pos*20
		y1=y+(20*h)
		ctx.strokeRect(0,y, 200, y1)
		if div==4:
			ctx.moveTo(0,y+(y1-y)/2)
			ctx.lineTo(200,y+(y1-y)/2)
		if div==2 or div==4:
			ctx.moveTo(200/2, y)
			ctx.lineTo(200/2, y1)
		ctx.stroke()
		

r  = Rack(20)
r.putUnit(0,2,4	)

document["listahost"] <= r
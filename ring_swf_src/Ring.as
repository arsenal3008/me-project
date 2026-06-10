package {
    import flash.display.Sprite;
    import flash.display.StageScaleMode;
    import flash.display.StageAlign;
    import flash.events.Event;
    import flash.external.ExternalInterface;

    /**
     * MOD_MRD reload ring — single parametric, self-rotating SWF that replaces
     * the 117 pre-rendered PNG frames (green/red/squad x 39).
     *
     * Public API (read by GUIFlash either as direct member assignment on
     * comp.movie.<name> OR via comp.movie.invoke('setX', value)):
     *   color      : uint    RGB tint (0xRRGGBB)      default white
     *   ringSize   : Number  diameter in px           default 80
     *   dotCount   : int     dots around the circle   default 60
     *   dotRadius  : Number  max dot radius in px      default 4
     *   progress   : Number  head phase 0..1 (manual) default 0
     *   animSpeed  : Number  auto-spin per frame 0..1  default 0.012
     *   tail       : Number  comet tail length 0..1    default 0.78
     *   minAlpha   : Number  faint-tail alpha 0..1     default 0.0
     * Invoke callbacks: ping(), setColor(int), setProgress(Number),
     *   setSize(Number), setSpeed(Number).
     */
    public dynamic class Ring extends Sprite {

        public var color:uint     = 0xFFFFFF;
        public var ringSize:Number = 80;
        public var dotCount:int   = 60;
        public var dotRadius:Number = 4;
        public var progress:Number = 0.0;
        public var animSpeed:Number = 0.012;
        public var tail:Number    = 0.78;
        public var minAlpha:Number = 0.0;

        private var _gfx:Sprite;
        private var _phase:Number = 0.0;

        public function Ring() {
            if (stage) _init(); else addEventListener(Event.ADDED_TO_STAGE, _init);
        }

        private function _init(e:Event = null):void {
            removeEventListener(Event.ADDED_TO_STAGE, _init);
            try {
                stage.scaleMode = StageScaleMode.NO_SCALE;
                stage.align = StageAlign.TOP_LEFT;
            } catch (err:*) {}
            _gfx = new Sprite();
            addChild(_gfx);
            _registerBridge();
            addEventListener(Event.ENTER_FRAME, _onFrame);
            _redraw();
        }

        private function _registerBridge():void {
            try {
                ExternalInterface.addCallback("ping",        _ping);
                ExternalInterface.addCallback("setColor",    _setColor);
                ExternalInterface.addCallback("setProgress", _setProgress);
                ExternalInterface.addCallback("setSize",     _setSize);
                ExternalInterface.addCallback("setSpeed",    _setSpeed);
            } catch (err:*) {}
        }

        private function _ping(... a):String { return "pong"; }
        private function _setColor(c:* = null):void { if (c != null) color = uint(c); }
        private function _setProgress(p:* = null):void { if (p != null) progress = Number(p); }
        private function _setSize(s:* = null):void { if (s != null) ringSize = Number(s); }
        private function _setSpeed(s:* = null):void { if (s != null) animSpeed = Number(s); }

        private function _onFrame(e:Event):void {
            _phase += animSpeed;
            if (_phase >= 1.0) _phase -= int(_phase);
            _redraw();
        }

        private function _redraw():void {
            var g:* = _gfx.graphics;
            g.clear();

            var n:int = dotCount > 1 ? dotCount : 1;
            var diam:Number = ringSize > 0 ? ringSize : 80;
            var dr:Number = dotRadius > 0 ? dotRadius : Math.max(2.0, diam / 20.0);
            var cx:Number = diam / 2.0;
            var cy:Number = diam / 2.0;
            var R:Number = diam / 2.0 - dr;
            if (R < dr) R = diam / 2.0;

            var head:Number = (progress + _phase) % 1.0;
            if (head < 0) head += 1.0;
            var tl:Number = (tail > 0 && tail <= 1) ? tail : 0.78;

            for (var i:int = 0; i < n; i++) {
                var t:Number = i / n;                 // 0..1 around circle
                var d:Number = head - t;              // distance behind head
                if (d < 0) d += 1.0;
                var f:Number = 1.0 - d / tl;          // brightness falloff
                var a:Number;
                var rad:Number;
                if (f <= 0) {
                    a = minAlpha;
                    rad = dr * 0.30;
                    if (a <= 0) continue;
                } else {
                    a = minAlpha + (1.0 - minAlpha) * f;
                    rad = dr * (0.30 + 0.70 * f);
                }
                var ang:Number = t * 2.0 * Math.PI - Math.PI / 2.0;
                var x:Number = cx + R * Math.cos(ang);
                var y:Number = cy + R * Math.sin(ang);
                g.beginFill(color, a);
                g.drawCircle(x, y, rad);
                g.endFill();
            }
        }
    }
}

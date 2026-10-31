import { r as registerInstance } from './index-001d5b4b.js';

var __classPrivateFieldGet = (undefined && undefined.__classPrivateFieldGet) || function (receiver, state, kind, f) {
  if (kind === "a" && !f)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var __classPrivateFieldSet = (undefined && undefined.__classPrivateFieldSet) || function (receiver, state, value, kind, f) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return (kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value)), value;
};
var _PageExposure_setupTimeout, _PageExposure_captureTimeout, _PageExposure_seenPortion, _PageExposure_relativeScrollPosition, _PageExposure_pageInterceptionRatio, _PageExposure_io;
const PageExposure = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    _PageExposure_setupTimeout.set(this, void 0);
    _PageExposure_captureTimeout.set(this, void 0);
    _PageExposure_seenPortion.set(this, 0);
    _PageExposure_relativeScrollPosition.set(this, 0);
    _PageExposure_pageInterceptionRatio.set(this, 0);
    _PageExposure_io.set(this, void 0);
    this.captureDebounce = 500;
    this.setup = this.setup.bind(this);
    this.onScroll = this.onScroll.bind(this);
    this.onBeforeUnload = this.onBeforeUnload.bind(this);
    this.track = this.track.bind(this);
  }
  componentDidLoad() {
    var _a;
    if (!window.IntersectionObserver) {
      return;
    }
    (_a = this.router) === null || _a === void 0 ? void 0 : _a.onChange('url', () => {
      this.start();
    });
    this.start();
  }
  reset() {
    var _a;
    clearTimeout(__classPrivateFieldGet(this, _PageExposure_setupTimeout, "f"));
    clearTimeout(__classPrivateFieldGet(this, _PageExposure_captureTimeout, "f"));
    __classPrivateFieldSet(this, _PageExposure_seenPortion, 0, "f");
    __classPrivateFieldSet(this, _PageExposure_relativeScrollPosition, 0, "f");
    __classPrivateFieldSet(this, _PageExposure_pageInterceptionRatio, 0, "f");
    document.removeEventListener('scroll', this.onScroll);
    window.removeEventListener('beforeunload', this.onBeforeUnload);
    (_a = __classPrivateFieldGet(this, _PageExposure_io, "f")) === null || _a === void 0 ? void 0 : _a.unobserve(document.body);
  }
  start() {
    this.reset();
    __classPrivateFieldSet(this, _PageExposure_setupTimeout, setTimeout(this.setup, 1000), "f");
  }
  setup() {
    // Tracking on beforeunload event only works if (matomo) beacons are activated!
    window.addEventListener('beforeunload', this.onBeforeUnload);
    document.addEventListener('scroll', this.onScroll);
    __classPrivateFieldSet(this, _PageExposure_io, new IntersectionObserver(([{ intersectionRatio }]) => {
      __classPrivateFieldSet(this, _PageExposure_pageInterceptionRatio, intersectionRatio, "f");
      this.capture();
    }, {
      threshold: new Array(101).fill(null).map((_, i) => i / 100),
    }), "f");
    __classPrivateFieldGet(this, _PageExposure_io, "f").observe(document.body);
  }
  capture() {
    window.clearTimeout(__classPrivateFieldGet(this, _PageExposure_captureTimeout, "f"));
    __classPrivateFieldSet(this, _PageExposure_captureTimeout, setTimeout(() => {
      const ratio = __classPrivateFieldGet(this, _PageExposure_pageInterceptionRatio, "f");
      const seenPortion = Math.round(Math.min(Math.max(__classPrivateFieldGet(this, _PageExposure_relativeScrollPosition, "f") * ratio + ratio, 0), 1) * 10) * 10;
      if (__classPrivateFieldGet(this, _PageExposure_seenPortion, "f") < seenPortion) {
        __classPrivateFieldSet(this, _PageExposure_seenPortion, seenPortion, "f");
        this.track(seenPortion);
      }
    }, this.captureDebounce), "f");
  }
  onBeforeUnload() {
    this.track(__classPrivateFieldGet(this, _PageExposure_seenPortion, "f"));
  }
  onScroll() {
    __classPrivateFieldSet(this, _PageExposure_relativeScrollPosition, window.pageYOffset / window.innerHeight, "f");
    this.capture();
  }
};
_PageExposure_setupTimeout = new WeakMap(), _PageExposure_captureTimeout = new WeakMap(), _PageExposure_seenPortion = new WeakMap(), _PageExposure_relativeScrollPosition = new WeakMap(), _PageExposure_pageInterceptionRatio = new WeakMap(), _PageExposure_io = new WeakMap();

export { PageExposure as d4l_page_exposure };

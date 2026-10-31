import { r as registerInstance } from './index-001d5b4b.js';

const Analytics = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
  }
  updateProductsMappingId(productsMappingId) {
    var _a;
    this.permitAnalytics &&
      this.productsDimensionId &&
      ((_a = window._paq) === null || _a === void 0 ? void 0 : _a.push([
        'setCustomDimension',
        this.productsDimensionId,
        productsMappingId,
      ]));
  }
  updateProjectsMappingId(projectsMappingId) {
    var _a;
    this.permitAnalytics &&
      this.projectsDimensionId &&
      ((_a = window._paq) === null || _a === void 0 ? void 0 : _a.push([
        'setCustomDimension',
        this.projectsDimensionId,
        projectsMappingId,
      ]));
  }
  componentWillLoad() {
    this.populateAnalyticsScript();
  }
  componentWillUpdate() {
    this.populateAnalyticsScript();
  }
  populateAnalyticsScript() {
    var _a;
    const script = document.getElementById(this.analyticsScriptId);
    if (script) {
      if (this.permitAnalytics && this.siteId) {
        // tracker methods like "setCustomDimension" should be called before "trackPageView"
        script.innerHTML = `
          var _paq = window._paq || [];
          ${this.productsDimensionId && this.projectsDimensionId
          ? `_paq.push(['setCustomDimension', ${this.productsDimensionId}, ${this.productsMappingId}]);`
          : ''}
          ${this.projectsDimensionId && this.projectsMappingId
          ? `_paq.push(['setCustomDimension', ${this.projectsDimensionId}, ${this.projectsMappingId}]);`
          : ''}
          ${this.isCrossDomainLinking
          ? `_paq.push(['enableCrossDomainLinking']);`
          : ''}
          ${((_a = this.crossDomains) === null || _a === void 0 ? void 0 : _a.length)
          ? `_paq.push(['setDomains', [${this.crossDomains.map((domain) => `"${domain}"`)}]]);`
          : ''}
          ${this.cookieDomain
          ? `_paq.push(['setCookieDomain', '${this.cookieDomain}']);`
          : ''}
          ${this.isHeartBeatTimer ? `_paq.push(['enableHeartBeatTimer']);` : ''}
          ${this.isRequireConsent ? `_paq.push(['requireConsent']);` : ''}
          _paq.push(['alwaysUseSendBeacon']);
          ${this.isCookieless ? `_paq.push(['disableCookies']);` : ''}
          _paq.push(['trackPageView']);
          _paq.push(['enableLinkTracking']);
          (function() {
            var u="${this.matomoUrl}";
            _paq.push(['setTrackerUrl', u+'matomo.php']);
            _paq.push(['setSiteId', '${this.siteId}']);
            var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
            g.type='text/javascript'; g.async=true; g.defer=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
            g.onload = function() {
              window.dispatchEvent(new CustomEvent('changePAQ', { detail: window._paq }));
            };
          })();
        `;
      }
      else {
        script.innerHTML = '';
      }
    }
  }
  static get watchers() { return {
    "productsMappingId": ["updateProductsMappingId"],
    "projectsMappingId": ["updateProjectsMappingId"]
  }; }
};

export { Analytics as d4l_analytics };

import { r as registerInstance, h } from './index-001d5b4b.js';
import { R as Route } from './index-13b9ea17.js';

const currentPathMatches = (pathMatcher) => {
  const matches = document.location.pathname.match(pathMatcher);
  if (matches !== null && matches.length > 0) {
    return matches.slice(1);
  }
  return undefined;
};
const StaticRedirect = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
  }
  render() {
    const { from, to } = this;
    const matches = currentPathMatches(from);
    if (matches !== undefined) {
      const targetURL = to(...matches);
      return h(Route, { path: "/", to: targetURL });
    }
    return null;
  }
};

export { StaticRedirect as d4l_static_redirect };

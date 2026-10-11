/*
 * Pinterest native Surge response adapter.
 * Original Loon rules: https://kelee.one/Tool/Loon/Lpx/Pinterest_remove_ads.lpx
 * Original rule author: 可莉🅥 https://github.com/luestr/ProxyResource
 * Manual Surge adaptation: WhiteSoulss/wool_scripts, 2026-10-11.
 *
 * Scope is the original two endpoints and top-level data array only.
 * Unlike the old strict jq whitelist, unidentified records and unexpected
 * response shapes pass through. Only explicit promoted=true/"true" is removed.
 * No requests, status codes, headers, pagination fields or nested data change.
 */
(function () {
  var result = {};
  try {
    result = rewrite();
  } catch (_) {
    // Malformed JSON or an unexpected value must not break the response.
  }
  $done(result);

  function hasUnsafeNumber(value) {
    if (typeof value === "number") {
      return !isFinite(value) ||
        (Math.floor(value) === value && Math.abs(value) > 9007199254740991);
    }
    if (!value || typeof value !== "object") return false;
    return Object.keys(value).some(function (key) { return hasUnsafeNumber(value[key]); });
  }

  function rewrite() {
    if (typeof $request !== "object" || !$request ||
        typeof $response !== "object" || !$response) return {};
    var url = $request.url;
    if (typeof url !== "string" ||
        !/^https:\/\/api\.pinterest\.com\/v\d\/(?:feeds\/home|pins\/\d+\/related\/modules)\/\?/i.test(url)) return {};
    if ($request.method && $request.method.toUpperCase() !== "GET") return {};
    if (typeof $response.status === "number" &&
        ($response.status < 200 || $response.status >= 300)) return {};
    if (typeof $response.body !== "string" || !$response.body) return {};

    var payload = JSON.parse($response.body);
    if (!payload || typeof payload !== "object" ||
        Array.isArray(payload) || !Array.isArray(payload.data)) return {};
    if (typeof payload.status === "string" && payload.status.toLowerCase() !== "success") return {};
    // JSON.parse/stringify must not round an unsafe numeric identifier.
    if (hasUnsafeNumber(payload)) return {};
    var filtered = payload.data.filter(function (item) {
      return !(item && typeof item === "object" && !Array.isArray(item) &&
               (item.is_promoted === true || item.is_promoted === "true"));
    });
    if (filtered.length === payload.data.length) return {};
    payload.data = filtered;
    return {body: JSON.stringify(payload)};
  }
})();

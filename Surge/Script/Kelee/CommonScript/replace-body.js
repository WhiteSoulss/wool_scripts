// Compatibility replacement for the unavailable original replace-body dependency.
// Input: regex->replacement. Used by the original Tencent Video plugin.
const separator = String($argument || '').indexOf('->');
if (separator < 0) {
  $done({});
} else {
  const pattern = $argument.slice(0, separator);
  const replacement = $argument.slice(separator + 2);
  const current = typeof $request !== 'undefined' ? $request : $response;
  const body = String(current.body || '').replace(new RegExp(pattern), replacement);
  $done({body});
}

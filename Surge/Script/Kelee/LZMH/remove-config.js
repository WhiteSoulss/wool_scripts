// Native Surge response script: implement Loon response.json.delete("value.config").
// Leave non-JSON and unrelated responses unchanged.
try {
  const payload = JSON.parse($response.body);
  if (payload && payload.value && typeof payload.value === 'object' &&
      Object.prototype.hasOwnProperty.call(payload.value, 'config')) {
    delete payload.value.config;
    $done({body: JSON.stringify(payload)});
  } else {
    $done({});
  }
} catch (_) {
  $done({});
}

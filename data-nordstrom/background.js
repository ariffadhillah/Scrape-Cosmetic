var config = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "http",
        host: "82.26.218.177", // Bagian HOST
        port: 6485            // Bagian PORT
      },
      bypassList: ["<-loopback>"]
    }
  };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "arssrhsq",    // GANTI: Username Proxy
            password: "x1vpi09f4v1g"  // GANTI: Password Proxy
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
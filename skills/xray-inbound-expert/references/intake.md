# Intake for an existing Ubuntu panel

Gather the smallest set of inputs that changes the result. Read available panel configuration first using authorized access; do not repeat information already supplied.

## Ask together when unknown

In Persian, a useful first question is:

> دامنه یا ساب‌دامنه‌ها را همراه وضعیت ابر نارنجی روشن/خاموش بنویسید. چند پروفایل اتصال متفاوت می‌خواهید و برای چه کلاینت‌هایی؟ این تعداد برای یک کاربر است یا چند کاربر جدا؟

Ask which Iranian networks/ISPs and whether stability, speed, or direct/CDN diversity matters when that choice affects the design. The project default is stability and client compatibility; state this as an assumption if the user gives no priority, not as a measured winner.

## Discover or obtain

| Input | Why it matters |
| --- | --- |
| Exact panel URL, custom base path, and locally available credentials | API access; panel path and inbound client endpoint are separate. |
| Panel version, actual core version, client app/core versions | Supported protocol, field names, transports, and export formats. |
| Existing inbounds, affected clients, full Xray template, and process state | Avoid duplicate ports, destructive replacement, and broken panel routing. |
| Origin IPv4/IPv6 and exposed listener ports | Select reachable endpoints and avoid an unusable AAAA route. |
| Domain inventory per hostname | A/AAAA/CNAME target, orange/gray cloud state, role, ownership, and existing certificate availability. |
| Existing reverse proxy and any occupied HTTPS listener | Sharing port 443 requires an existing compatible dispatch design. |
| Profile count versus users and listeners | Multiple share links need not mean multiple inbounds; preserve intended identity and quota semantics. |

For each hostname, record `client endpoint`, `origin`, `SNI`, `HTTP Host`, or `REALITY target` as applicable. A REALITY target need not be owned by the user; an owned origin/CDN hostname has different certificate and routing requirements.

For an orange-cloud path, ask only the needed SSL mode, origin TLS/certificate details, WebSocket/gRPC availability, and relevant WAF/challenge/redirect behavior. Do not request Cloudflare credentials unless a separately requested Cloudflare action needs them. Ordinary DNS output does not prove all account proxy settings, especially with CNAME chains; use supplied settings or authorized account reads.

If the user says "three configs", clarify whether that means three transport alternatives, three users, or three client-app exports. If fewer viable architectures exist, explain that and propose the achievable set instead of making incompatible or redundant listeners to fill the count.

No SSH account is necessary for API-only work. Local access becomes relevant for confirmed existing key/certificate files, key generation, port inventory unavailable in the panel, or protected file snapshots. Lack of SSH does not authorize fabricating these details.

import os

# Define the file structure and content
files = {
    "assets/products.json": """[
  {
    "sku": "pillow_cool1",
    "name": "Cooling Gel Pillow",
    "brand": "RestCo",
    "price": "89.99",
    "aff_url": "https://example.com/aff/pillow1",
    "image": "/images/pillow1.jpg",
    "category": "pillow",
    "features": ["gel-infused", "removable cover", "machine washable"]
  },
  {
    "sku": "noise_wm1",
    "name": "White Noise Machine Lite",
    "brand": "SleepBox",
    "price": "39.99",
    "aff_url": "https://example.com/aff/noise1",
    "image": "/images/noise1.jpg",
    "category": "noise",
    "features": ["10 sounds", "timer", "usb power"]
  }
]""",

    "layouts/shortcodes/product.html": """{{- $sku := .Get "sku" -}}
{{- $data := resources.Get "products.json" | transform.Unmarshal -}}
{{- $product := index (where $data "sku" $sku) 0 -}}

{{- if $product -}}
<div class="product-card">
  <div class="product-image">
    <img src="{{ $product.image }}" alt="{{ $product.name }}" loading="lazy">
  </div>
  <div class="product-details">
    <h3>{{ $product.name }} <span class="brand">by {{ $product.brand }}</span></h3>
    <ul class="features">
      {{ range $product.features }}
      <li>{{ . }}</li>
      {{ end }}
    </ul>
    <div class="price-action">
      <span class="price">${{ $product.price }}</span>
      <a href="{{ $product.aff_url }}" class="btn-buy" rel="sponsored noopener" target="_blank">Check Price</a>
    </div>
  </div>
</div>
{{- else -}}
  {{- warnf "Product SKU '%s' not found in assets/products.json" $sku -}}
{{- end -}}""",

    "layouts/_default/baseof.html": """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ if .IsHome }}{{ site.Title }}{{ else }}{{ .Title }} | {{ site.Title }}{{ end }}</title>
  <meta name="description" content="{{ .Params.description | default site.Params.site_description }}">
  <style>
    body { font-family: system-ui, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }
    header, footer { padding: 20px 0; border-bottom: 1px solid #eee; margin-bottom: 20px; }
    nav a { margin-right: 15px; text-decoration: none; color: #0066cc; font-weight: bold; }
    .product-card { display: flex; gap: 20px; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin: 30px 0; background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .product-image img { max-width: 150px; border-radius: 4px; }
    .product-details h3 { margin-top: 0; }
    .brand { font-weight: normal; font-size: 0.9em; color: #666; }
    .features { padding-left: 20px; font-size: 0.9em; color: #555; }
    .price-action { margin-top: 15px; display: flex; align-items: center; gap: 15px; }
    .price { font-size: 1.25em; font-weight: bold; color: #222; }
    .btn-buy { background: #0066cc; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-weight: bold; }
    .btn-buy:hover { background: #004c99; }
  </style>
</head>
<body>
  <header>
    <nav>
      <a href="/">{{ site.Title }}</a>
      <a href="/posts/">Reviews</a>
    </nav>
  </header>
  <main>
    {{ block "main" . }}{{ end }}
  </main>
  <footer>
    <p>&copy; {{ now.Year }} {{ site.Title }}</p>
  </footer>
</body>
</html>""",

    "layouts/_default/single.html": """{{ define "main" }}
<article>
  <header>
    <h1>{{ .Title }}</h1>
    {{ if .Date }}<time style="color:#666; font-size:0.9em;">{{ .Date.Format "January 2, 2006" }}</time>{{ end }}
  </header>
  <div class="content">
    {{ .Content }}
  </div>
</article>
{{ end }}""",

    "content/posts/test-automation.md": """---
title: "The Best Cooling Pillows of 2025"
date: 2025-10-25
draft: false
description: "We tested the top cooling pillows so you don't have to."
---

Sleeping hot is a nightmare. Here is our top recommendation for side sleepers.

## Top Pick: RestCo Cooling Gel

We selected this pillow because of its unique phase-change material.

{{< product sku="pillow_cool1" >}}

## Budget Pick: White Noise

If you need sound masking instead of cooling, check this out.

{{< product sku="noise_wm1" >}}

## Conclusion
Getting good rest requires the right gear.
"""
}

# Clean old attempts and write new files
print("--- Fixing Site Structure ---")
for file_path, content in files.items():
    # Create directory if missing
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write the file
    with open(file_path, "w") as f:
        f.write(content)
    print(f"✅ Created: {file_path}")

print("\n🎉 Site structure repaired. You can run Hugo now.")

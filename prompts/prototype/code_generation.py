"""Prompts for HTML/CSS wireframe code generation"""

GENERATE_HTML_CSS_PROMPT = """
You are an expert frontend developer. Generate clean HTML and CSS code for a wireframe based on this mockup.

**Project Context:**
- Project: {project_name}
- Page: {page_name}
- Goal: {project_goal}

**Mockup Description:**
{mockup_description}

**Requirements:**
- Framework: {framework}
- Responsive: Yes (mobile-first)
- Accessibility: WCAG 2.1 AA compliant
- Clean, semantic HTML5
- Modern CSS (Flexbox/Grid)

**Your Task:**
Generate production-ready HTML and CSS code that recreates this mockup as a functional wireframe.

**Output Format:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name} - {project_name}</title>
    <style>
        /* CSS code here */
    </style>
</head>
<body>
    <!-- HTML structure here -->
</body>
</html>
```

**Guidelines:**
1. Use semantic HTML elements
2. Include proper ARIA labels for accessibility
3. Use CSS custom properties for colors
4. Make it responsive (mobile-first approach)
5. Include hover states for interactive elements
6. Use modern CSS (no floats, use Flexbox/Grid)
7. Add comments to explain sections
8. Keep it clean and maintainable

Generate complete, working code that can be saved as a single HTML file and opened in a browser.
"""

GENERATE_TAILWIND_HTML_PROMPT = """
You are an expert frontend developer. Generate HTML with Tailwind CSS classes for a wireframe.

**Project Context:**
- Project: {project_name}
- Page: {page_name}

**Mockup Description:**
{mockup_description}

**Requirements:**
- Use Tailwind CSS via CDN
- Responsive classes (mobile-first)
- Accessibility attributes
- Modern, clean design

**Output Format:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name} - {project_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- Tailwind HTML here -->
</body>
</html>
```

Use appropriate Tailwind utility classes for layout, spacing, colors, and typography.
Make it production-ready and visually polished.
"""

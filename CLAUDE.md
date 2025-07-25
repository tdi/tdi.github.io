# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo-based static blog site for documenting a CTO's learning journey into blockchain and Web3 technology. The site uses the PaperMod theme and is deployed to GitHub Pages at https://tdi.github.io.

## Development Environment

The project uses Nix flakes for development environment management:
- `nix develop` - Enter development shell with Hugo available
- The dev shell includes Hugo and sets a custom prompt `[dev] $PS1`

## Common Commands

### Building and Serving
- `hugo server` - Start development server with live reload (typically on port 1313)
- `hugo server -D` - Start server including draft posts
- `hugo` - Build static site to `public/` directory
- `hugo --buildDrafts` - Build including draft posts

### Content Management
- `hugo new posts/post-name.md` - Create new blog post
- `hugo new content/page-name.md` - Create new page

### Deployment
The `public/` directory contains the built static site and should be committed to deploy to GitHub Pages.

## Site Architecture

### Configuration
- `hugo.toml` - Main Hugo configuration file
- Uses PaperMod theme from `themes/PaperMod/` (git submodule)
- Configured for production deployment to https://tdi.github.io

### Content Structure
- `content/posts/` - Blog posts in Markdown format
- `content/about.md` - About page
- `content/search.md` - Search functionality page
- `static/` - Static assets (images, etc.)
- `layouts/partials/extend_head.html` - Custom head extensions

### Blog Post Format
Posts use Hugo front matter with these key fields:
```yaml
---
title: "Post Title"
date: 2025-05-28T10:00:00+01:00
draft: false  # Set to true for drafts
tags: ["blockchain", "learning"]
categories: ["Learning Journey"]
author: "Darek Dwornikowski"
showToc: true
description: "Post description for SEO"
---
```

### Theme Customization
- Using PaperMod theme with custom configuration
- Site branding: "Darek's Blog" - CTO learning blockchain
- Configured with social icons (Twitter, GitHub, LinkedIn)
- Search functionality enabled with Fuse.js
- Analytics and SEO optimization configured

## Site Features
- Responsive design with light/dark theme toggle
- Search functionality
- Categories and tags
- Reading time estimation
- Social sharing buttons
- Table of contents for posts
- RSS feeds
- SEO optimization with OpenGraph and Twitter Cards
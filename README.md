# awesome-bof
## About awesome-bof
> 🧠 The ultimate, community-curated resource for Beacon Object Files (BOFs) — tutorials, how-tos, deep dives, and reference materials.

## 🎯 Goals
**Be the go-to source for everything related to BOFs**
- Help both Red and Blue Teams understand the mechanics of BOFs
- Make BOF development, testing and execution even more accessible
- Find public BOF projects, tools, loaders, research and training

---

### 🧪 Tutorials — *Learning by Doing*
- [Building Your First BOF](./tutorials/tutorial-building-your-first-bof.md)

### 🛠️ How-To Guides — *Solving Specific Tasks*
- [Set Up Visual Studio for BOF Development](./how-to/setup-visual-studio-bof.md)
- [Excute BOFs in C2 frameworks](./how-to/how-to-execute-bofs-in-c2.md) 
- [Running BOFs Asynchronously in Cobalt Strike](./how-to/how-to-async-execute.md)

### 📖 Explanation — *Understanding Concepts*
- [What are BOFs?](./explanation/explanation-what-are-bofs.md)
- [C2 Framework BOF Support](./reference/c2-framework-bof-support.md)
- [BOF Internals: Structure, API, Lifecycle](./explanation/bof-internals-explained.md)
- [BOF Loaders and Execution Engines](./explanation/bof_loader_explainer.md)

### 🧾 Reference — *Reliable Information Lookups*
- [Public BOF Repositories Catalog](./reference/bofs-catalog.md)
- [BOF and COFF loaders](./reference/loaders-catalog.md)
- [C2 Framework BOF Support](./reference/c2-framework-bof-support.md)
- [Reference: Developer Tooling & Templates](./reference/reference-bof-dev.md)
- [Blog Posts and Research on BOF Development](./reference/bof-blogs-and-research.md)
- [BOF training courses](./reference/bof-training-courses.md)

---

## Community todo list
These are articles where changes are appropriate, or not yet written. Hopefully the community would like to contribute to this project by tackling any of these or other ideas for the project.

### Change ideas
- Continue expanding the [Public BOF Repositories Catalog](./reference/bofs-catalog.md) with new BOFs coming out
- Expand the [Public BOF Repositories Catalog](./reference/bofs-catalog.md) with Sliver extensions and BOFs written for Havoc
- Expand [Execute BOFs in C2 frameworks](./how-to/how-to-execute-bofs-in-c2.md) with more detail for each C2 framework

### New article ideas
- How-to article on intermediate level BOF development
- How-to article on advanced BOF development
- How-to article on writing aggressor scripts for BOF support in CS
- How-to article on writing scripts for BOF support in Sliver and Havoc
- How-to article for developing and running BOF.NET BOFs 

## 🤝 Contributing
Want to update a reference page with new BOFs? Or write a new article? Or make changes?
- Open a pull request
- Follow the structure of the article in the relevant folder (`tutorials/`, `how-to/`, etc.)
- Include links, descriptions, and credit where due
- Or, submit an issue with whatever you would like to see changed

This repo thrives on contributions from both red and blue teams in the community. I hope we can apply the structure I have created to add new information as it appears. The entire project is written in markdown, making it easy for anyone to fork, modify and submit pull requests or issues.

*Note*: I have used AI to help me write and structure some the articles. I have reviewed all the information, but if mistakes have snuck in, its probably this human's fault, rather than AI slop. Again however, issues and pull requests are very welcome to correct any wrong information. 

---

## About Diátaxis
This project follow the approach of the [Diátaxis](https://diataxis.fr/) documentation framework. Diátaxis identifies four distinct needs, and four corresponding forms of documentation - tutorials, how-to guides, technical reference and explanation. All articles in this repository if therefore organised around the structures of those needs. This ensures high-quality, easy to discover and use documentation.

![Diátaxis framework](./resources/diataxis.png)

---

## Credit
- All the awesome BOF and loader developers that publish their BOFs on Github
- The Cobalt Strike team for pushing the direction of BOF development since 2020 
- TrustedSec for all their awesome blog posts, BOF collections and training
- Zero-point for their awesome course on BOF development

## ⚖️ License
This project is licensed under [](./LICENSE). Attribution encouraged when citing.

const DEFAULT_LANGUAGE = "zh-CN";
const PAGE = document.body.dataset.page || "home";

const SUPPORTED_LANGUAGES = [
  { code: "zh-CN", label: "\u7b80\u4f53\u4e2d\u6587" },
  { code: "en", label: "English" },
  { code: "es", label: "Espanol" },
  { code: "fr", label: "Francais" },
  { code: "de", label: "Deutsch" },
  { code: "ja", label: "\u65e5\u672c\u8a9e" },
  { code: "ko", label: "\ud55c\uad6d\uc5b4" },
  { code: "pt-BR", label: "Portugues" },
  { code: "ru", label: "\u0420\u0443\u0441\u0441\u043a\u0438\u0439" },
  { code: "ar", label: "\u0627\u0644\u0639\u0631\u0628\u064a\u0629" },
  { code: "hi", label: "\u0939\u093f\u0928\u094d\u0926\u0940" },
];

const PAGE_TO_NAV = {
  home: "home",
  auth: "auth",
  problems: "problems",
  "problem-detail": "problems",
  submit: "submit",
  submissions: "submissions",
  admin: "admin",
};

const PAGE_META = {
  home: { title: "meta.homeTitle", description: "meta.homeDescription" },
  auth: { title: "meta.authTitle", description: "meta.authDescription" },
  problems: { title: "meta.problemsTitle", description: "meta.problemsDescription" },
  "problem-detail": { title: "meta.problemTitle", description: "meta.problemDescription" },
  submit: { title: "meta.submitTitle", description: "meta.submitDescription" },
  submissions: { title: "meta.submissionsTitle", description: "meta.submissionsDescription" },
  admin: { title: "meta.adminTitle", description: "meta.adminDescription" },
};

const LANGUAGE_ALIASES = {
  zh: "zh-CN",
  "zh-hans": "zh-CN",
  en: "en",
  es: "es",
  fr: "fr",
  de: "de",
  ja: "ja",
  ko: "ko",
  pt: "pt-BR",
  ru: "ru",
  ar: "ar",
  hi: "hi",
};

const RTL_LANGUAGES = new Set(["ar"]);

const DEMO_PROBLEM_TRANSLATIONS = {
  "zh-CN": {
    "sum-two-numbers": {
      title: "\u4e24\u6570\u6c42\u548c",
      description: "\u4ece\u6807\u51c6\u8f93\u5165\u8bfb\u53d6\u4e24\u4e2a\u6574\u6570 a \u548c b\uff0c\u8f93\u51fa\u5b83\u4eec\u7684\u548c\u3002\u4e24\u4e2a\u6574\u6570\u90fd\u5728 64 \u4f4d\u6709\u7b26\u53f7\u6574\u6570\u8303\u56f4\u5185\u3002",
      input_description: "\u4e00\u884c\uff0c\u5305\u542b\u4e24\u4e2a\u4ee5\u7a7a\u683c\u5206\u9694\u7684\u6574\u6570 a \u548c b\u3002",
      output_description: "\u8f93\u51fa\u4e00\u4e2a\u6574\u6570 a + b\u3002",
    },
    "word-counter": {
      title: "\u5355\u8bcd\u8ba1\u6570",
      description: "\u8bfb\u53d6\u5168\u90e8\u8f93\u5165\u6587\u672c\uff0c\u7edf\u8ba1\u5176\u4e2d\u5355\u8bcd\u7684\u6570\u91cf\u3002\u5355\u8bcd\u5b9a\u4e49\u4e3a\u7531\u975e\u7a7a\u767d\u5b57\u7b26\u7ec4\u6210\u7684\u6700\u957f\u8fde\u7eed\u7247\u6bb5\u3002",
      input_description: "\u4e00\u884c\u6216\u591a\u884c\u6587\u672c\u3002",
      output_description: "\u8f93\u51fa\u5355\u8bcd\u603b\u6570\u3002",
    },
    "distinct-sort": {
      title: "\u53bb\u91cd\u6392\u5e8f",
      description: "\u7ed9\u5b9a n \u4e2a\u6574\u6570\uff0c\u53bb\u9664\u91cd\u590d\u503c\u540e\u6309\u5347\u5e8f\u6392\u5e8f\uff0c\u5e76\u5728\u4e00\u884c\u4e2d\u7528\u7a7a\u683c\u8f93\u51fa\u3002",
      input_description: "\u7b2c\u4e00\u884c\u5305\u542b\u6574\u6570 n\u3002\u7b2c\u4e8c\u884c\u5305\u542b n \u4e2a\u6574\u6570\u3002",
      output_description: "\u6309\u5347\u5e8f\u8f93\u51fa\u53bb\u91cd\u540e\u7684\u6574\u6570\uff0c\u6570\u5b57\u4e4b\u95f4\u7528\u7a7a\u683c\u5206\u9694\u3002",
    },
    "balanced-brackets": {
      title: "\u62ec\u53f7\u662f\u5426\u5e73\u8861",
      description: "\u7ed9\u5b9a\u4e00\u4e2a\u4ec5\u7531 (), [] \u548c {} \u7ec4\u6210\u7684\u5b57\u7b26\u4e32\uff0c\u5224\u65ad\u62ec\u53f7\u662f\u5426\u5e73\u8861\u3002\u82e5\u5e73\u8861\u8f93\u51fa YES\uff0c\u5426\u5219\u8f93\u51fa NO\u3002",
      input_description: "\u4e00\u884c\u62ec\u53f7\u5b57\u7b26\u4e32\u3002",
      output_description: "\u8f93\u51fa YES \u6216 NO\u3002",
    },
    "climbing-stairs-mod": {
      title: "\u722c\u697c\u68af\u53d6\u6a21",
      description: "\u4f60\u7ad9\u5728\u7b2c 0 \u7ea7\u53f0\u9636\uff0c\u8981\u5230\u8fbe\u7b2c n \u7ea7\u3002\u6bcf\u6b21\u53ef\u4ee5\u5411\u4e0a\u8d70 1 \u7ea7\u6216 2 \u7ea7\u3002\u6c42\u4e0d\u540c\u8d70\u6cd5\u7684\u6570\u91cf\uff0c\u5e76\u5bf9 1000000007 \u53d6\u6a21\u3002",
      input_description: "\u4e00\u4e2a\u6574\u6570 n\u3002",
      output_description: "\u8f93\u51fa\u8d70\u6cd5\u603b\u6570\u5bf9 1000000007 \u53d6\u6a21\u540e\u7684\u7ed3\u679c\u3002",
    },
  },
};

const translations = {
  en: {
    meta: {
      homeTitle: "Online Judge System",
      homeDescription: "A multi-page online judge frontend for browsing problems, submitting solutions, reviewing verdicts, and managing content.",
      authTitle: "Auth - Online Judge System",
      authDescription: "Sign in or create an account for the online judge system.",
      problemsTitle: "Problems - Online Judge System",
      problemsDescription: "Browse public problems on a dedicated archive page.",
      problemTitle: "Problem Detail - Online Judge System",
      problemDescription: "Read a single problem statement on a dedicated page.",
      submitTitle: "Submit Solution - Online Judge System",
      submitDescription: "Submit code on a dedicated editor page.",
      submissionsTitle: "Submissions - Online Judge System",
      submissionsDescription: "Inspect submission history and detailed verdicts.",
      adminTitle: "Admin - Online Judge System",
      adminDescription: "Manage problems, test cases, and user roles from a dedicated admin page.",
    },
    nav: {
      stack: "FastAPI + Redis + PostgreSQL",
      brand: "Online Judge System",
      home: "Home",
      auth: "Auth",
      problems: "Problems",
      submit: "Submit",
      submissions: "Submissions",
      admin: "Admin",
      language: "Language",
    },
    health: {
      checking: "Checking API",
      onlinePill: "API healthy",
      offlinePill: "API offline",
      healthy: "Healthy",
      offline: "Offline",
      booting: "Booting",
    },
    session: {
      guest: "Guest",
      guestHint: "Browse public features without signing in.",
      signIn: "Sign in",
      logout: "Log out",
      account: "Account",
      roleAdmin: "Admin",
      roleUser: "User",
    },
    metrics: {
      api: "API status",
      problems: "Public problems",
      submissions: "Recent submissions",
      session: "Session",
    },
    home: {
      eyebrow: "System overview",
      title: "Online judge portal",
      text: "A multi-page frontend for account management, problem browsing, statement viewing, solution submission, verdict review, and administration.",
      ctaProblems: "Explore problems",
      ctaSubmit: "Open submit page",
      featuredEyebrow: "Problem set",
      featuredTitle: "Public problem archive",
      viewAll: "View all",
      pagesEyebrow: "Modules",
      pagesTitle: "Functional entry points",
      pageAuth: "Account authentication and session management.",
      pageProblems: "Public problem retrieval and filtering.",
      pageStatementTitle: "Problem detail",
      pageStatement: "Dedicated statement and metadata view.",
      pageSubmit: "Code entry and submission queue integration.",
      pageSubmissions: "Submission history and detailed verdict review.",
      pageAdmin: "Problem maintenance, test case input, and role management.",
    },
    auth: {
      username: "Username",
      email: "Email",
      password: "Password",
      loginAction: "Login",
      registerAction: "Create account",
      loginSuccess: "Login successful. Your session is ready.",
      registerSuccess: "Account created. You can sign in now.",
      logoutSuccess: "You are back in guest mode.",
      loginFailed: "Invalid username or password.",
    },
    authPage: {
      eyebrow: "Identity",
      title: "Authentication",
      text: "Account registration and login are handled on a standalone page.",
      loginEyebrow: "Login",
      loginTitle: "Sign in to your workspace",
      registerEyebrow: "Register",
      registerTitle: "Create a new account",
      feedbackEyebrow: "Status",
      feedbackTitle: "Session feedback",
    },
    problems: {
      search: "Search",
      searchPlaceholder: "Find by title",
      difficulty: "Difficulty",
      all: "All",
      empty: "No public problems match this filter yet.",
    },
    problemsPage: {
      eyebrow: "Problem archive",
      title: "Problem archive",
      text: "Centralized public problem listing with search and difficulty filtering.",
      filtersEyebrow: "Filters",
      filtersTitle: "Search the public catalog",
      sideEyebrow: "Structure",
      sideTitle: "Module relations",
      stepOneTitle: "Problem detail page",
      stepOneText: "Statement content is displayed in an isolated detail module.",
      stepTwoTitle: "Submission page",
      stepTwoText: "Code input and queue submission are handled in a separate editor module.",
      stepThreeTitle: "Verdict page",
      stepThreeText: "Detailed run results are reviewed in the submissions module.",
      resultCount: "{count} problems loaded",
    },
    statement: {
      timeLimit: "Time limit",
      memoryLimit: "Memory limit",
      visibility: "Visibility",
      description: "Description",
      input: "Input",
      output: "Output",
      sampleInput: "Sample input",
      sampleOutput: "Sample output",
      noDescription: "No description provided.",
      noInput: "No input description provided.",
      noOutput: "No output description provided.",
      noSample: "No sample provided.",
    },
    problemPage: {
      eyebrow: "Statement",
      placeholderTitle: "Select a problem from the archive.",
      text: "Dedicated statement page for problem content and execution constraints.",
      back: "Back to problems",
      submit: "Solve this problem",
      noSelection: "No selection",
      slugNone: "slug: none",
      placeholderBody: "Open a problem to load its statement.",
      sideEyebrow: "Context",
      sideTitle: "Page role",
      sideOneTitle: "Statement scope",
      sideOneText: "This module presents the problem description, limits, and sample data.",
      sideTwoTitle: "Submission handoff",
      sideTwoText: "Solution editing and queueing are handled in the submit module.",
      introLoaded: "Statement page for {title}.",
      missingSlug: "No problem slug was provided in the URL.",
    },
    submitPage: {
      eyebrow: "Submission editor",
      title: "Submission workspace",
      text: "Dedicated code input page for target selection, template loading, and queue submission.",
      formEyebrow: "Editor",
      formTitle: "Queue a new solution",
      noTarget: "Target: none",
      resultEyebrow: "Latest result",
      resultTitle: "Queue feedback",
      resultEmpty: "Submit a solution to see its live verdict summary here.",
      latestTitle: "Latest submission",
    },
    editor: {
      problemSlug: "Problem slug",
      problemSlugPlaceholder: "Enter a problem slug",
      codeEditor: "Code editor",
      loginHint: "Login to unlock submissions.",
      authedHint: "Authenticated. You can queue Python code now.",
      loadTemplate: "Load template",
      submit: "Submit solution",
      noAuth: "You need to login before submitting code.",
      slugRequired: "Select or enter a problem slug first.",
      queueSuccess: "Submission queued: {id}",
      templateLine1: "# Read from stdin and write to stdout.",
      templateLine2: "# Problem slug: {slug}",
    },
    submissionsPage: {
      eyebrow: "Verdict history",
      title: "Submission records",
      text: "Centralized history view for verdict status, runtime metrics, and per-test results.",
      feedEyebrow: "Feed",
      feedTitle: "Recent submissions",
      detailEyebrow: "Detail",
      detailTitle: "Pick a submission",
      detailEmpty: "Open a submission from the feed to inspect its summary.",
      allStatuses: "All statuses",
      loginPrompt: "Login to load your personal submission feed.",
      noSubmissions: "No submissions yet. Use the submit page to queue one.",
    },
    detail: {
      noRuntimeError: "No runtime error captured.",
      noResults: "No per-test results yet.",
      testLabel: "Test {index}",
      noErrorMessage: "No error message.",
    },
    adminPage: {
      eyebrow: "Administration",
      title: "Administration console",
      text: "Administrative page for problem creation, test case maintenance, and user role management.",
      accessEyebrow: "Access",
      accessTitle: "Admin access check",
      accessDenied: "Login as an admin to use this page.",
      accessGranted: "Admin session ready.",
      problemEyebrow: "Problem creation",
      problemTitle: "Create a public problem",
      problemName: "Title",
      problemSlug: "Slug",
      problemPublic: "Make problem public immediately",
      createProblem: "Create problem",
      createProblemSuccess: "Problem created: {slug}",
      testCaseEyebrow: "Test cases",
      testCaseTitle: "Attach a test case",
      testOrder: "Order",
      testSample: "Mark as sample",
      createTestCase: "Create test case",
      createTestCaseSuccess: "Test case created for {slug}",
      usersEyebrow: "User management",
      usersTitle: "Promote or demote roles",
      changeRole: "Change role",
      roleUpdated: "Role updated for {username}",
      noUsers: "No users found.",
    },
    common: {
      refresh: "Refresh",
      ms: "{value} ms",
      kb: "{value} KB",
      passed: "{passed}/{total} passed",
      target: "Target: {slug}",
      slug: "slug: {slug}",
    },
    visibility: {
      public: "Public",
      private: "Private",
    },
    difficulty: {
      easy: "Easy",
      medium: "Medium",
      hard: "Hard",
    },
    status: {
      accepted: "Accepted",
      pending: "Pending",
      running: "Running",
      wrong_answer: "Wrong answer",
      time_limit_exceeded: "Time limit exceeded",
      runtime_error: "Runtime error",
      memory_limit_exceeded: "Memory limit exceeded",
      compilation_error: "Compilation error",
      failed: "Failed",
    },
  },
  "zh-CN": {
    meta: {
      homeTitle: "\u5728\u7ebf\u5224\u9898\u7cfb\u7edf",
      homeDescription: "\u4e00\u4e2a\u6309\u5de5\u4f5c\u6d41\u7a0b\u62c6\u9875\u7684\u5728\u7ebf\u5224\u9898\u591a\u9875\u9762\u524d\u7aef\u3002",
      authTitle: "\u767b\u5f55\u4e0e\u6ce8\u518c - \u5728\u7ebf\u5224\u9898\u7cfb\u7edf",
      authDescription: "\u5728\u72ec\u7acb\u9875\u9762\u5b8c\u6210\u767b\u5f55\u6216\u6ce8\u518c\u3002",
      problemsTitle: "\u9898\u5e93 - \u5728\u7ebf\u5224\u9898\u7cfb\u7edf",
      problemsDescription: "\u5728\u72ec\u7acb\u9898\u5e93\u9875\u9762\u6d4f\u89c8\u516c\u5f00\u9898\u76ee\u3002",
      problemTitle: "\u9898\u76ee\u8be6\u60c5 - \u5728\u7ebf\u5224\u9898\u7cfb\u7edf",
      problemDescription: "\u5728\u4e13\u5c5e\u9875\u9762\u9605\u8bfb\u5355\u9898\u9898\u9762\u3002",
      submitTitle: "\u63d0\u4ea4\u89e3\u7b54 - \u5728\u7ebf\u5224\u9898\u7cfb\u7edf",
      submitDescription: "\u5728\u72ec\u7acb\u7f16\u8f91\u9875\u4e2d\u63d0\u4ea4\u4ee3\u7801\u3002",
      submissionsTitle: "\u63d0\u4ea4\u8bb0\u5f55 - \u5728\u7ebf\u5224\u9898\u7cfb\u7edf",
      submissionsDescription: "\u67e5\u770b\u5386\u53f2\u63d0\u4ea4\u548c\u8be6\u7ec6\u5224\u9898\u7ed3\u679c\u3002",
      adminTitle: "\u7ba1\u7406\u540e\u53f0 - \u5728\u7ebf\u5224\u9898\u7cfb\u7edf",
      adminDescription: "\u5728\u72ec\u7acb\u7ba1\u7406\u9875\u9762\u5904\u7406\u9898\u76ee\u3001\u6d4b\u8bd5\u70b9\u548c\u7528\u6237\u89d2\u8272\u3002",
    },
    nav: {
      stack: "FastAPI + Redis + PostgreSQL",
      brand: "\u5728\u7ebf\u5224\u9898\u7cfb\u7edf",
      home: "\u9996\u9875",
      auth: "\u8d26\u53f7",
      problems: "\u9898\u5e93",
      submit: "\u63d0\u4ea4",
      submissions: "\u8bb0\u5f55",
      admin: "\u7ba1\u7406",
      language: "\u8bed\u8a00",
    },
    health: {
      checking: "\u6b63\u5728\u68c0\u67e5 API",
      onlinePill: "API \u6b63\u5e38",
      offlinePill: "API \u79bb\u7ebf",
      healthy: "\u6b63\u5e38",
      offline: "\u79bb\u7ebf",
      booting: "\u542f\u52a8\u4e2d",
    },
    session: {
      guest: "\u6e38\u5ba2",
      guestHint: "\u65e0\u9700\u767b\u5f55\u5373\u53ef\u4f7f\u7528\u516c\u5f00\u529f\u80fd\u3002",
      signIn: "\u767b\u5f55",
      logout: "\u9000\u51fa",
      account: "\u8d26\u53f7",
      roleAdmin: "\u7ba1\u7406\u5458",
      roleUser: "\u7528\u6237",
    },
    metrics: {
      api: "API \u72b6\u6001",
      problems: "\u516c\u5f00\u9898\u76ee",
      submissions: "\u6700\u8fd1\u63d0\u4ea4",
      session: "\u5f53\u524d\u4f1a\u8bdd",
    },
    home: {
      eyebrow: "\u7cfb\u7edf\u6982\u89c8",
      title: "\u5728\u7ebf\u5224\u9898\u95e8\u6237",
      text: "\u8fd9\u662f\u4e00\u4e2a\u7528\u4e8e\u8d26\u53f7\u7ba1\u7406\u3001\u9898\u76ee\u6d4f\u89c8\u3001\u9898\u9762\u67e5\u770b\u3001\u89e3\u7b54\u63d0\u4ea4\u3001\u7ed3\u679c\u590d\u67e5\u4e0e\u7cfb\u7edf\u7ba1\u7406\u7684\u591a\u9875\u524d\u7aef\u3002",
      ctaProblems: "\u6d4f\u89c8\u9898\u5e93",
      ctaSubmit: "\u6253\u5f00\u63d0\u4ea4\u9875",
      featuredEyebrow: "\u9898\u5e93",
      featuredTitle: "\u516c\u5f00\u9898\u76ee\u6863\u6848",
      viewAll: "\u67e5\u770b\u5168\u90e8",
      pagesEyebrow: "\u6a21\u5757",
      pagesTitle: "\u529f\u80fd\u5165\u53e3",
      pageAuth: "\u8d26\u53f7\u8ba4\u8bc1\u4e0e\u4f1a\u8bdd\u7ba1\u7406\u3002",
      pageProblems: "\u516c\u5f00\u9898\u5e93\u68c0\u7d22\u4e0e\u7b5b\u9009\u3002",
      pageStatementTitle: "\u9898\u76ee\u8be6\u60c5",
      pageStatement: "\u72ec\u7acb\u9898\u9762\u4e0e\u5143\u4fe1\u606f\u67e5\u770b\u9875\u3002",
      pageSubmit: "\u4ee3\u7801\u7f16\u5199\u4e0e\u63d0\u4ea4\u961f\u5217\u5bf9\u63a5\u3002",
      pageSubmissions: "\u63d0\u4ea4\u5386\u53f2\u4e0e\u5224\u9898\u7ed3\u679c\u590d\u67e5\u3002",
      pageAdmin: "\u9898\u76ee\u7ef4\u62a4\u3001\u6d4b\u8bd5\u70b9\u5f55\u5165\u4e0e\u89d2\u8272\u7ba1\u7406\u3002",
    },
    auth: {
      username: "\u7528\u6237\u540d",
      email: "\u90ae\u7bb1",
      password: "\u5bc6\u7801",
      loginAction: "\u767b\u5f55",
      registerAction: "\u521b\u5efa\u8d26\u53f7",
      loginSuccess: "\u767b\u5f55\u6210\u529f\uff0c\u4f1a\u8bdd\u5df2\u5c31\u7eea\u3002",
      registerSuccess: "\u6ce8\u518c\u6210\u529f\uff0c\u73b0\u5728\u53ef\u4ee5\u767b\u5f55\u4e86\u3002",
      logoutSuccess: "\u4f60\u5df2\u56de\u5230\u6e38\u5ba2\u6a21\u5f0f\u3002",
      loginFailed: "\u7528\u6237\u540d\u6216\u5bc6\u7801\u4e0d\u6b63\u786e\u3002",
    },
    authPage: {
      eyebrow: "\u8eab\u4efd",
      title: "\u8d26\u53f7\u8ba4\u8bc1",
      text: "\u7528\u4e8e\u5b8c\u6210\u6ce8\u518c\u3001\u767b\u5f55\u548c\u4f1a\u8bdd\u521d\u59cb\u5316\u7684\u72ec\u7acb\u9875\u9762\u3002",
      loginEyebrow: "\u767b\u5f55",
      loginTitle: "\u767b\u5f55\u4f60\u7684\u5de5\u4f5c\u533a",
      registerEyebrow: "\u6ce8\u518c",
      registerTitle: "\u521b\u5efa\u65b0\u8d26\u53f7",
      feedbackEyebrow: "\u72b6\u6001",
      feedbackTitle: "\u4f1a\u8bdd\u53cd\u9988",
    },
    problems: {
      search: "\u641c\u7d22",
      searchPlaceholder: "\u6309\u6807\u9898\u641c\u7d22",
      difficulty: "\u96be\u5ea6",
      all: "\u5168\u90e8",
      empty: "\u6682\u65f6\u6ca1\u6709\u7b26\u5408\u6761\u4ef6\u7684\u516c\u5f00\u9898\u76ee\u3002",
    },
    problemsPage: {
      eyebrow: "\u9898\u5e93\u6863\u6848",
      title: "\u516c\u5f00\u9898\u5e93",
      text: "\u7528\u4e8e\u9898\u76ee\u68c0\u7d22\u3001\u7b5b\u9009\u548c\u5217\u8868\u5c55\u793a\u7684\u96c6\u4e2d\u9875\u9762\u3002",
      filtersEyebrow: "\u7b5b\u9009",
      filtersTitle: "\u641c\u7d22\u516c\u5f00\u9898\u5e93",
      sideEyebrow: "\u7ed3\u6784",
      sideTitle: "\u6a21\u5757\u5173\u7cfb",
      stepOneTitle: "\u9898\u76ee\u8be6\u60c5\u9875",
      stepOneText: "\u9898\u9762\u5185\u5bb9\u5728\u72ec\u7acb\u8be6\u60c5\u6a21\u5757\u4e2d\u5c55\u793a\u3002",
      stepTwoTitle: "\u63d0\u4ea4\u9875",
      stepTwoText: "\u4ee3\u7801\u7f16\u5199\u4e0e\u63d0\u4ea4\u961f\u5217\u7531\u72ec\u7acb\u7f16\u8f91\u6a21\u5757\u5904\u7406\u3002",
      stepThreeTitle: "\u7ed3\u679c\u9875",
      stepThreeText: "\u8be6\u7ec6\u8fd0\u884c\u7ed3\u679c\u5728\u63d0\u4ea4\u8bb0\u5f55\u6a21\u5757\u4e2d\u67e5\u770b\u3002",
      resultCount: "\u5df2\u52a0\u8f7d {count} \u9053\u9898\u76ee",
    },
    statement: {
      timeLimit: "\u65f6\u95f4\u9650\u5236",
      memoryLimit: "\u5185\u5b58\u9650\u5236",
      visibility: "\u53ef\u89c1\u6027",
      description: "\u9898\u76ee\u63cf\u8ff0",
      input: "\u8f93\u5165\u8bf4\u660e",
      output: "\u8f93\u51fa\u8bf4\u660e",
      sampleInput: "\u6837\u4f8b\u8f93\u5165",
      sampleOutput: "\u6837\u4f8b\u8f93\u51fa",
      noDescription: "\u6682\u65e0\u9898\u76ee\u63cf\u8ff0\u3002",
      noInput: "\u6682\u65e0\u8f93\u5165\u8bf4\u660e\u3002",
      noOutput: "\u6682\u65e0\u8f93\u51fa\u8bf4\u660e\u3002",
      noSample: "\u6682\u65e0\u6837\u4f8b\u3002",
    },
    problemPage: {
      eyebrow: "\u9898\u9762",
      placeholderTitle: "\u8bf7\u4ece\u9898\u5e93\u4e2d\u9009\u62e9\u9898\u76ee\u3002",
      text: "\u7528\u4e8e\u5c55\u793a\u9898\u9762\u5185\u5bb9\u3001\u8fd0\u884c\u9650\u5236\u548c\u6837\u4f8b\u6570\u636e\u7684\u72ec\u7acb\u9875\u9762\u3002",
      back: "\u8fd4\u56de\u9898\u5e93",
      submit: "\u53bb\u89e3\u8fd9\u9053\u9898",
      noSelection: "\u672a\u9009\u62e9",
      slugNone: "slug\uff1a\u65e0",
      placeholderBody: "\u6253\u5f00\u4e00\u9053\u9898\u76ee\u540e\uff0c\u8fd9\u91cc\u4f1a\u52a0\u8f7d\u9898\u9762\u3002",
      sideEyebrow: "\u4e0a\u4e0b\u6587",
      sideTitle: "\u9875\u9762\u89d2\u8272",
      sideOneTitle: "\u9898\u9762\u8303\u56f4",
      sideOneText: "\u672c\u6a21\u5757\u8d1f\u8d23\u9898\u76ee\u63cf\u8ff0\u3001\u9650\u5236\u6761\u4ef6\u4e0e\u6837\u4f8b\u6570\u636e\u5c55\u793a\u3002",
      sideTwoTitle: "\u63d0\u4ea4\u5207\u6362",
      sideTwoText: "\u89e3\u7b54\u7f16\u5199\u4e0e\u961f\u5217\u63d0\u4ea4\u7531\u63d0\u4ea4\u6a21\u5757\u5904\u7406\u3002",
      introLoaded: "\u5f53\u524d\u6b63\u5728\u67e5\u770b {title} \u7684\u9898\u9762\u3002",
      missingSlug: "URL \u4e2d\u6ca1\u6709\u5e26\u9898\u76ee slug\u3002",
    },
    submitPage: {
      eyebrow: "\u63d0\u4ea4\u7f16\u8f91\u533a",
      title: "\u63d0\u4ea4\u5de5\u4f5c\u533a",
      text: "\u7528\u4e8e\u76ee\u6807\u9009\u62e9\u3001\u6a21\u677f\u52a0\u8f7d\u3001\u4ee3\u7801\u8f93\u5165\u4e0e\u961f\u5217\u63d0\u4ea4\u7684\u4e13\u7528\u9875\u9762\u3002",
      formEyebrow: "\u7f16\u8f91\u5668",
      formTitle: "\u53d1\u8d77\u4e00\u6b21\u65b0\u63d0\u4ea4",
      noTarget: "\u76ee\u6807\uff1a\u672a\u9009\u62e9",
      resultEyebrow: "\u6700\u65b0\u7ed3\u679c",
      resultTitle: "\u961f\u5217\u53cd\u9988",
      resultEmpty: "\u63d0\u4ea4\u4e00\u6b21\u89e3\u7b54\u540e\uff0c\u8fd9\u91cc\u4f1a\u663e\u793a\u5b9e\u65f6\u5224\u9898\u6982\u8981\u3002",
      latestTitle: "\u6700\u65b0\u63d0\u4ea4",
    },
    editor: {
      problemSlug: "\u9898\u76ee slug",
      problemSlugPlaceholder: "\u8f93\u5165\u9898\u76ee slug",
      codeEditor: "\u4ee3\u7801\u7f16\u8f91\u5668",
      loginHint: "\u767b\u5f55\u540e\u624d\u80fd\u63d0\u4ea4\u4ee3\u7801\u3002",
      authedHint: "\u5df2\u8ba4\u8bc1\uff0c\u73b0\u5728\u53ef\u4ee5\u63d0\u4ea4 Python \u4ee3\u7801\u3002",
      loadTemplate: "\u52a0\u8f7d\u6a21\u677f",
      submit: "\u63d0\u4ea4\u89e3\u7b54",
      noAuth: "\u63d0\u4ea4\u4ee3\u7801\u524d\u9700\u8981\u5148\u767b\u5f55\u3002",
      slugRequired: "\u8bf7\u5148\u9009\u62e9\u6216\u8f93\u5165\u9898\u76ee slug\u3002",
      queueSuccess: "\u63d0\u4ea4\u5df2\u5165\u961f\uff1a{id}",
      templateLine1: "# \u4ece stdin \u8bfb\u53d6\uff0c\u5411 stdout \u8f93\u51fa\u3002",
      templateLine2: "# \u9898\u76ee slug\uff1a{slug}",
    },
    submissionsPage: {
      eyebrow: "\u5224\u9898\u5386\u53f2",
      title: "\u63d0\u4ea4\u8bb0\u5f55",
      text: "\u7528\u4e8e\u67e5\u770b\u5224\u9898\u72b6\u6001\u3001\u8fd0\u884c\u6307\u6807\u548c\u6bcf\u4e2a\u6d4b\u8bd5\u70b9\u7ed3\u679c\u7684\u96c6\u4e2d\u9875\u9762\u3002",
      feedEyebrow: "\u5217\u8868",
      feedTitle: "\u6700\u8fd1\u63d0\u4ea4",
      detailEyebrow: "\u8be6\u60c5",
      detailTitle: "\u9009\u62e9\u4e00\u6761\u63d0\u4ea4",
      detailEmpty: "\u4ece\u5217\u8868\u4e2d\u6253\u5f00\u4e00\u6761\u63d0\u4ea4\u540e\uff0c\u8fd9\u91cc\u4f1a\u663e\u793a\u6982\u8981\u4fe1\u606f\u3002",
      allStatuses: "\u5168\u90e8\u72b6\u6001",
      loginPrompt: "\u767b\u5f55\u540e\u624d\u80fd\u67e5\u770b\u4f60\u7684\u63d0\u4ea4\u8bb0\u5f55\u3002",
      noSubmissions: "\u6682\u65f6\u8fd8\u6ca1\u6709\u63d0\u4ea4\uff0c\u53ef\u4ee5\u5148\u53bb\u63d0\u4ea4\u9875\u53d1\u8d77\u4e00\u6b21\u89e3\u7b54\u3002",
    },
    detail: {
      noRuntimeError: "\u6ca1\u6709\u6355\u83b7\u5230\u8fd0\u884c\u65f6\u9519\u8bef\u3002",
      noResults: "\u6682\u65e0\u6bcf\u4e2a\u6d4b\u8bd5\u70b9\u7684\u7ed3\u679c\u3002",
      testLabel: "\u6d4b\u8bd5\u70b9 {index}",
      noErrorMessage: "\u6ca1\u6709\u9519\u8bef\u4fe1\u606f\u3002",
    },
    adminPage: {
      eyebrow: "\u7cfb\u7edf\u7ba1\u7406",
      title: "\u7ba1\u7406\u63a7\u5236\u53f0",
      text: "\u7528\u4e8e\u9898\u76ee\u521b\u5efa\u3001\u6d4b\u8bd5\u70b9\u7ef4\u62a4\u4e0e\u7528\u6237\u89d2\u8272\u7ba1\u7406\u7684\u884c\u653f\u9875\u9762\u3002",
      accessEyebrow: "\u6743\u9650",
      accessTitle: "\u7ba1\u7406\u5458\u68c0\u67e5",
      accessDenied: "\u8bf7\u4f7f\u7528\u7ba1\u7406\u5458\u8d26\u53f7\u767b\u5f55\u540e\u518d\u4f7f\u7528\u6b64\u9875\u3002",
      accessGranted: "\u5df2\u8fdb\u5165\u7ba1\u7406\u5458\u4f1a\u8bdd\u3002",
      problemEyebrow: "\u521b\u5efa\u9898\u76ee",
      problemTitle: "\u521b\u5efa\u4e00\u9053\u516c\u5f00\u9898\u76ee",
      problemName: "\u6807\u9898",
      problemSlug: "Slug",
      problemPublic: "\u7acb\u5373\u5c06\u9898\u76ee\u8bbe\u4e3a\u516c\u5f00",
      createProblem: "\u521b\u5efa\u9898\u76ee",
      createProblemSuccess: "\u9898\u76ee\u5df2\u521b\u5efa\uff1a{slug}",
      testCaseEyebrow: "\u6d4b\u8bd5\u70b9",
      testCaseTitle: "\u4e3a\u9898\u76ee\u6dfb\u52a0\u6d4b\u8bd5\u70b9",
      testOrder: "\u987a\u5e8f",
      testSample: "\u6807\u8bb0\u4e3a\u6837\u4f8b",
      createTestCase: "\u521b\u5efa\u6d4b\u8bd5\u70b9",
      createTestCaseSuccess: "\u5df2\u4e3a {slug} \u521b\u5efa\u6d4b\u8bd5\u70b9",
      usersEyebrow: "\u7528\u6237\u7ba1\u7406",
      usersTitle: "\u63d0\u5347\u6216\u964d\u7ea7\u89d2\u8272",
      changeRole: "\u66f4\u6539\u89d2\u8272",
      roleUpdated: "\u5df2\u66f4\u65b0 {username} \u7684\u89d2\u8272",
      noUsers: "\u6682\u65f6\u6ca1\u6709\u7528\u6237\u3002",
    },
    common: {
      refresh: "\u5237\u65b0",
      ms: "{value} \u6beb\u79d2",
      kb: "{value} KB",
      passed: "\u901a\u8fc7 {passed}/{total}",
      target: "\u76ee\u6807\uff1a{slug}",
      slug: "slug\uff1a{slug}",
    },
    visibility: {
      public: "\u516c\u5f00",
      private: "\u79c1\u6709",
    },
    difficulty: {
      easy: "\u7b80\u5355",
      medium: "\u4e2d\u7b49",
      hard: "\u56f0\u96be",
    },
    status: {
      accepted: "\u901a\u8fc7",
      pending: "\u7b49\u5f85\u4e2d",
      running: "\u8fd0\u884c\u4e2d",
      wrong_answer: "\u7b54\u6848\u9519\u8bef",
      time_limit_exceeded: "\u8d85\u65f6",
      runtime_error: "\u8fd0\u884c\u9519\u8bef",
      memory_limit_exceeded: "\u5185\u5b58\u8d85\u9650",
      compilation_error: "\u7f16\u8bd1\u9519\u8bef",
      failed: "\u5931\u8d25",
    },
  },
};

const state = {
  token: localStorage.getItem("oj_token") || "",
  user: loadStoredJson("oj_user"),
  language: resolveLanguage(localStorage.getItem("oj_language") || detectLanguage()),
  apiHealth: "booting",
  problems: [],
  selectedProblem: null,
  submissions: [],
  selectedSubmission: null,
  pollTimer: null,
};

const elements = {
  pageDescription: document.getElementById("page-description"),
  languageSelect: document.getElementById("language-select"),
  healthPill: document.getElementById("health-pill"),
  sessionName: document.getElementById("session-name"),
  sessionRole: document.getElementById("session-role"),
  authLink: document.getElementById("auth-link"),
  logoutButton: document.getElementById("logout-button"),
};

document.addEventListener("DOMContentLoaded", async () => {
  buildLanguageOptions();
  bindGlobalEvents();
  activateNav();
  applyLanguage(state.language, false);
  syncHeader();
  await loadHealth();
  await initializePage();
});

function buildLanguageOptions() {
  if (!elements.languageSelect) {
    return;
  }
  elements.languageSelect.innerHTML = SUPPORTED_LANGUAGES.map(
    (language) => `<option value="${escapeHtml(language.code)}">${escapeHtml(language.label)}</option>`
  ).join("");
  elements.languageSelect.value = state.language;
}

function bindGlobalEvents() {
  if (elements.languageSelect) {
    elements.languageSelect.addEventListener("change", (event) => {
      applyLanguage(event.currentTarget.value);
    });
  }
  if (elements.logoutButton) {
    elements.logoutButton.addEventListener("click", logout);
  }
}

function activateNav() {
  const current = PAGE_TO_NAV[PAGE] || PAGE;
  document.querySelectorAll("[data-nav]").forEach((link) => {
    link.classList.toggle("active", link.dataset.nav === current);
  });
}

async function initializePage() {
  if (PAGE === "home") {
    await initHomePage();
    return;
  }
  if (PAGE === "auth") {
    initAuthPage();
    return;
  }
  if (PAGE === "problems") {
    await initProblemsPage();
    return;
  }
  if (PAGE === "problem-detail") {
    await initProblemDetailPage();
    return;
  }
  if (PAGE === "submit") {
    initSubmitPage();
    return;
  }
  if (PAGE === "submissions") {
    await initSubmissionsPage();
    return;
  }
  if (PAGE === "admin") {
    await initAdminPage();
  }
}

function applyLanguage(language, persist = true) {
  state.language = resolveLanguage(language);
  if (persist) {
    localStorage.setItem("oj_language", state.language);
  }

  document.documentElement.lang = state.language;
  document.documentElement.dir = RTL_LANGUAGES.has(state.language) ? "rtl" : "ltr";
  if (elements.languageSelect) {
    elements.languageSelect.value = state.language;
  }

  const meta = PAGE_META[PAGE] || PAGE_META.home;
  document.title = t(meta.title);
  if (elements.pageDescription) {
    elements.pageDescription.setAttribute("content", t(meta.description));
  }

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });

  syncHeader();
  renderHealth();

  if (PAGE === "home") {
    renderHomeState();
  } else if (PAGE === "problems") {
    renderProblemsPage();
  } else if (PAGE === "problem-detail") {
    renderProblemDetail();
  } else if (PAGE === "submit") {
    renderSubmitPage();
  } else if (PAGE === "submissions") {
    renderSubmissionsPage();
  } else if (PAGE === "admin") {
    renderAdminUsers();
    renderAdminGate();
  }
}

function syncHeader() {
  const loggedIn = Boolean(state.token && state.user);
  if (elements.sessionName) {
    elements.sessionName.textContent = loggedIn ? state.user.username : t("session.guest");
  }
  if (elements.sessionRole) {
    elements.sessionRole.textContent = loggedIn
      ? `${translateRole(state.user.role)} - ${state.user.email}`
      : t("session.guestHint");
  }
  if (elements.authLink) {
    elements.authLink.textContent = loggedIn ? t("session.account") : t("session.signIn");
    elements.authLink.href = "/auth";
    elements.authLink.classList.toggle("hidden", false);
  }
  if (elements.logoutButton) {
    elements.logoutButton.classList.toggle("hidden", !loggedIn);
  }
}

async function loadHealth() {
  try {
    await apiFetch("/api/v1/health");
    state.apiHealth = "healthy";
  } catch {
    state.apiHealth = "offline";
  }
  renderHealth();
}

function renderHealth() {
  if (!elements.healthPill) {
    return;
  }
  if (state.apiHealth === "healthy") {
    elements.healthPill.textContent = t("health.onlinePill");
    elements.healthPill.className = "status-chip success";
    return;
  }
  if (state.apiHealth === "offline") {
    elements.healthPill.textContent = t("health.offlinePill");
    elements.healthPill.className = "status-chip danger";
    return;
  }
  elements.healthPill.textContent = t("health.checking");
  elements.healthPill.className = "status-chip neutral";
}

async function initHomePage() {
  await loadProblemsIntoState();
  if (state.token) {
    await loadSubmissionsIntoState();
  }
  renderHomeState();
}

function renderHomeState() {
  const metricApi = document.getElementById("metric-api");
  const metricProblems = document.getElementById("metric-problems");
  const metricSubmissions = document.getElementById("metric-submissions");
  const metricSession = document.getElementById("metric-session");
  const featuredProblems = document.getElementById("featured-problems");

  if (metricApi) {
    metricApi.textContent = state.apiHealth === "healthy" ? t("health.healthy") : state.apiHealth === "offline" ? t("health.offline") : t("health.booting");
  }
  if (metricProblems) {
    metricProblems.textContent = String(state.problems.length);
  }
  if (metricSubmissions) {
    metricSubmissions.textContent = String(state.submissions.length);
  }
  if (metricSession) {
    metricSession.textContent = state.user ? translateRole(state.user.role) : t("session.guest");
  }
  if (featuredProblems) {
    const items = state.problems.slice(0, 4);
    if (!items.length) {
      featuredProblems.innerHTML = `<div class="empty-state">${escapeHtml(t("problems.empty"))}</div>`;
    } else {
      featuredProblems.innerHTML = items.map((problem) => renderProblemCard(problem)).join("");
      bindProblemCardLinks(featuredProblems);
    }
  }
}

function initAuthPage() {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
  }
  if (registerForm) {
    registerForm.addEventListener("submit", handleRegister);
  }
}

async function handleLogin(event) {
  event.preventDefault();
  const feedback = document.getElementById("auth-feedback");
  const formData = new FormData(event.currentTarget);
  const payload = Object.fromEntries(formData.entries());

  try {
    const data = await apiFetch("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    persistSession(data.access_token, data.user);
    syncHeader();
    setFeedback(feedback, t("auth.loginSuccess"), "success");
  } catch (error) {
    setFeedback(feedback, error.message || t("auth.loginFailed"), "error");
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const feedback = document.getElementById("auth-feedback");
  const formData = new FormData(event.currentTarget);
  const payload = Object.fromEntries(formData.entries());

  try {
    await apiFetch("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    event.currentTarget.reset();
    setFeedback(feedback, t("auth.registerSuccess"), "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function initProblemsPage() {
  const search = document.getElementById("problem-search");
  const difficulty = document.getElementById("problem-difficulty");
  const refresh = document.getElementById("refresh-problems");
  if (search) {
    search.addEventListener("input", debounce(loadProblemsWithFilters, 240));
  }
  if (difficulty) {
    difficulty.addEventListener("change", loadProblemsWithFilters);
  }
  if (refresh) {
    refresh.addEventListener("click", loadProblemsWithFilters);
  }
  await loadProblemsWithFilters();
}

async function loadProblemsWithFilters() {
  const search = document.getElementById("problem-search")?.value.trim() || "";
  const difficulty = document.getElementById("problem-difficulty")?.value || "";
  await loadProblemsIntoState(search, difficulty);
  renderProblemsPage();
}

async function loadProblemsIntoState(search = "", difficulty = "") {
  const params = new URLSearchParams({ page: "1", page_size: "20" });
  if (search) {
    params.set("search", search);
  }
  if (difficulty) {
    params.set("difficulty", difficulty);
  }
  try {
    const response = await apiFetch(`/api/v1/problems?${params.toString()}`);
    state.problems = response.items || [];
  } catch {
    state.problems = [];
  }
}

function renderProblemsPage() {
  const list = document.getElementById("problem-list");
  const count = document.getElementById("problem-count");
  if (count) {
    count.textContent = t("problemsPage.resultCount", { count: state.problems.length });
  }
  if (!list) {
    return;
  }
  if (!state.problems.length) {
    list.innerHTML = `<div class="empty-state">${escapeHtml(t("problems.empty"))}</div>`;
    return;
  }
  list.innerHTML = state.problems.map((problem) => renderProblemCard(problem)).join("");
  bindProblemCardLinks(list);
}

async function initProblemDetailPage() {
  const slug = new URLSearchParams(window.location.search).get("slug");
  if (!slug) {
    state.selectedProblem = null;
    renderProblemDetail();
    return;
  }
  try {
    const problem = await apiFetch(`/api/v1/problems/${slug}`);
    state.selectedProblem = problem;
  } catch {
    state.selectedProblem = null;
  }
  renderProblemDetail();
}

function renderProblemDetail() {
  const title = document.getElementById("problem-title");
  const intro = document.getElementById("problem-intro");
  const diff = document.getElementById("problem-difficulty-pill");
  const slugPill = document.getElementById("problem-slug-pill");
  const time = document.getElementById("problem-time-limit");
  const mem = document.getElementById("problem-memory-limit");
  const visibility = document.getElementById("problem-visibility");
  const desc = document.getElementById("problem-description");
  const input = document.getElementById("problem-input");
  const output = document.getElementById("problem-output");
  const sampleIn = document.getElementById("problem-sample-input");
  const sampleOut = document.getElementById("problem-sample-output");
  const submitLink = document.getElementById("problem-to-submit");

  if (!state.selectedProblem) {
    if (title) {
      title.textContent = t("problemPage.placeholderTitle");
    }
    if (intro) {
      intro.textContent = t("problemPage.missingSlug");
    }
    if (diff) {
      diff.textContent = t("problemPage.noSelection");
      diff.className = "status-chip neutral";
    }
    if (slugPill) {
      slugPill.textContent = t("problemPage.slugNone");
    }
    if (time) {
      time.textContent = "--";
    }
    if (mem) {
      mem.textContent = "--";
    }
    if (visibility) {
      visibility.textContent = "--";
    }
    if (desc) {
      desc.textContent = t("problemPage.placeholderBody");
    }
    if (input) {
      input.textContent = t("problemPage.placeholderBody");
    }
    if (output) {
      output.textContent = t("problemPage.placeholderBody");
    }
    if (sampleIn) {
      sampleIn.textContent = "--";
    }
    if (sampleOut) {
      sampleOut.textContent = "--";
    }
    if (submitLink) {
      submitLink.href = "/submit";
    }
    return;
  }

  const problem = localizeProblem(state.selectedProblem);
  if (title) {
    title.textContent = problem.title;
  }
  if (intro) {
    intro.textContent = t("problemPage.introLoaded", { title: problem.title });
  }
  if (diff) {
    diff.textContent = translateDifficulty(problem.difficulty);
    diff.className = `status-chip ${difficultyClass(problem.difficulty)}`;
  }
  if (slugPill) {
    slugPill.textContent = t("common.slug", { slug: problem.slug });
  }
  if (time) {
    time.textContent = t("common.ms", { value: problem.time_limit_ms });
  }
  if (mem) {
    mem.textContent = t("common.kb", { value: problem.memory_limit_kb });
  }
  if (visibility) {
    visibility.textContent = problem.is_public ? t("visibility.public") : t("visibility.private");
  }
  if (desc) {
    desc.textContent = problem.description || t("statement.noDescription");
  }
  if (input) {
    input.textContent = problem.input_description || t("statement.noInput");
  }
  if (output) {
    output.textContent = problem.output_description || t("statement.noOutput");
  }
  if (sampleIn) {
    sampleIn.textContent = problem.sample_input || t("statement.noSample");
  }
  if (sampleOut) {
    sampleOut.textContent = problem.sample_output || t("statement.noSample");
  }
  if (submitLink) {
    submitLink.href = `/submit?slug=${encodeURIComponent(problem.slug)}`;
  }
}

function initSubmitPage() {
  const slug = new URLSearchParams(window.location.search).get("slug");
  const slugInput = document.getElementById("manual-problem-slug");
  const editor = document.getElementById("code-editor");
  const templateButton = document.getElementById("load-template");
  const submitButton = document.getElementById("submit-code");

  if (slug && slugInput) {
    slugInput.value = slug;
  }
  if (editor && !editor.value.trim()) {
    editor.value = 'print("Ready to judge")';
  }
  if (templateButton) {
    templateButton.addEventListener("click", loadCodeTemplate);
  }
  if (submitButton) {
    submitButton.addEventListener("click", handleSubmit);
  }
  renderSubmitPage();
}

function renderSubmitPage() {
  const target = document.getElementById("editor-target");
  const hint = document.getElementById("editor-hint");
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "";
  if (target) {
    target.textContent = slug ? t("common.target", { slug }) : t("submitPage.noTarget");
  }
  if (hint) {
    hint.textContent = state.user ? t("editor.authedHint") : t("editor.loginHint");
  }
}

function loadCodeTemplate() {
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "problem-slug";
  const editor = document.getElementById("code-editor");
  if (!editor) {
    return;
  }
  editor.value = [
    "def solve() -> None:",
    `    ${t("editor.templateLine1")}`,
    `    ${t("editor.templateLine2", { slug })}`,
    "    pass",
    "",
    'if __name__ == "__main__":',
    "    solve()",
  ].join("\n");
}

async function handleSubmit() {
  const feedback = document.getElementById("submit-feedback");
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "";
  const code = document.getElementById("code-editor")?.value || "";
  if (!state.token) {
    setFeedback(feedback, t("editor.noAuth"), "error");
    return;
  }
  if (!slug) {
    setFeedback(feedback, t("editor.slugRequired"), "error");
    return;
  }
  try {
    const submission = await apiFetch("/api/v1/submissions", {
      method: "POST",
      body: JSON.stringify({ problem_slug: slug, code, language: "python" }),
    }, true);
    setFeedback(feedback, t("editor.queueSuccess", { id: submission.id }), "success");
    renderSubmitPage();
    await watchSingleSubmission(submission.id);
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function watchSingleSubmission(submissionId) {
  stopPolling();
  const card = document.getElementById("latest-submission-card");
  if (card) {
    card.className = "empty-state";
    card.textContent = `${t("submitPage.latestTitle")}: ${submissionId}`;
  }
  const tick = async () => {
    try {
      const detail = await apiFetch(`/api/v1/submissions/${submissionId}`, {}, true);
      state.selectedSubmission = detail;
      renderLatestSubmissionCard(detail);
      if (!["pending", "running"].includes(detail.status)) {
        stopPolling();
      }
    } catch (error) {
      renderLatestSubmissionCard(null, error.message);
      stopPolling();
    }
  };
  await tick();
  state.pollTimer = window.setInterval(tick, 2000);
}

function renderLatestSubmissionCard(submission, errorMessage = "") {
  const card = document.getElementById("latest-submission-card");
  if (!card) {
    return;
  }
  if (!submission) {
    card.className = "empty-state";
    card.textContent = errorMessage || t("submitPage.resultEmpty");
    return;
  }
  const title = localizeProblemTitle(submission.problem_slug, submission.problem_title || submission.problem_slug);
  card.className = "test-card";
  card.innerHTML = `
    <strong>${escapeHtml(title)}</strong>
    <p>${escapeHtml(translateStatus(submission.status))}</p>
    <div class="meta-row">
      <span class="status-chip ${statusClass(submission.status)}">${escapeHtml(translateStatus(submission.status))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.passed", { passed: submission.passed_test_cases, total: submission.total_test_cases }))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.ms", { value: Math.round(submission.max_execution_time_ms || 0) }))}</span>
    </div>
  `;
}

async function initSubmissionsPage() {
  const refresh = document.getElementById("refresh-submissions");
  const filter = document.getElementById("submission-status-filter");
  if (refresh) {
    refresh.addEventListener("click", loadSubmissionsPageData);
  }
  if (filter) {
    filter.addEventListener("change", loadSubmissionsPageData);
  }
  await loadSubmissionsPageData();
}

async function loadSubmissionsPageData() {
  if (!state.token) {
    state.submissions = [];
    state.selectedSubmission = null;
    renderSubmissionsPage();
    return;
  }
  const status = document.getElementById("submission-status-filter")?.value || "";
  await loadSubmissionsIntoState(status);
  renderSubmissionsPage();
  if (state.submissions.some((submission) => ["pending", "running"].includes(submission.status))) {
    startListPolling(loadSubmissionsPageData);
  } else {
    stopPolling();
  }
}

async function loadSubmissionsIntoState(status = "") {
  const params = new URLSearchParams({ page: "1", page_size: "20" });
  if (status) {
    params.set("status", status);
  }
  try {
    const response = await apiFetch(`/api/v1/submissions?${params.toString()}`, {}, true);
    state.submissions = response.items || [];
  } catch {
    state.submissions = [];
  }
}

function renderSubmissionsPage() {
  const list = document.getElementById("submission-list");
  if (!list) {
    return;
  }
  if (!state.token) {
    list.innerHTML = `<div class="empty-state">${escapeHtml(t("submissionsPage.loginPrompt"))}</div>`;
    renderSubmissionDetail(null);
    return;
  }
  if (!state.submissions.length) {
    list.innerHTML = `<div class="empty-state">${escapeHtml(t("submissionsPage.noSubmissions"))}</div>`;
    renderSubmissionDetail(null);
    return;
  }
  list.innerHTML = state.submissions.map((submission) => renderSubmissionCard(submission)).join("");
  list.querySelectorAll("[data-submission-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.getAttribute("data-submission-id");
      await openSubmissionDetail(id);
    });
  });
  if (!state.selectedSubmission && state.submissions[0]) {
    openSubmissionDetail(state.submissions[0].id);
  } else {
    renderSubmissionDetail(state.selectedSubmission);
  }
}

async function openSubmissionDetail(id) {
  try {
    const detail = await apiFetch(`/api/v1/submissions/${id}`, {}, true);
    state.selectedSubmission = detail;
    renderSubmissionsPage();
  } catch {
    renderSubmissionDetail(null);
  }
}

function renderSubmissionDetail(submission) {
  const title = document.getElementById("submission-detail-title");
  const summary = document.getElementById("submission-summary");
  const results = document.getElementById("test-results");
  if (!title || !summary || !results) {
    return;
  }
  if (!submission) {
    title.textContent = t("submissionsPage.detailTitle");
    summary.textContent = t("submissionsPage.detailEmpty");
    results.innerHTML = "";
    return;
  }
  const problemTitle = localizeProblemTitle(submission.problem_slug, submission.problem_title || submission.problem_slug);
  title.textContent = `${problemTitle} - ${translateStatus(submission.status)}`;
  summary.innerHTML = `
    <div class="meta-row">
      <span class="status-chip ${statusClass(submission.status)}">${escapeHtml(translateStatus(submission.status))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.passed", { passed: submission.passed_test_cases, total: submission.total_test_cases }))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.ms", { value: Math.round(submission.max_execution_time_ms || 0) }))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.kb", { value: Math.round(submission.max_memory_used_kb || 0) }))}</span>
    </div>
    <p>${escapeHtml(submission.error_message || t("detail.noRuntimeError"))}</p>
  `;
  if (!submission.test_results || !submission.test_results.length) {
    results.innerHTML = `<div class="empty-state">${escapeHtml(t("detail.noResults"))}</div>`;
    return;
  }
  results.innerHTML = submission.test_results
    .map((result, index) => `
      <article class="test-card">
        <strong>${escapeHtml(t("detail.testLabel", { index: index + 1 }))}</strong>
        <div class="meta-row">
          <span class="status-chip ${statusClass(result.status)}">${escapeHtml(translateStatus(result.status))}</span>
          <span class="status-chip neutral">${escapeHtml(t("common.ms", { value: Math.round(result.execution_time_ms || 0) }))}</span>
          <span class="status-chip neutral">${escapeHtml(t("common.kb", { value: Math.round(result.memory_used_kb || 0) }))}</span>
        </div>
        <p>${escapeHtml(result.error_message || t("detail.noErrorMessage"))}</p>
        ${result.output ? `<pre class="content-block">${escapeHtml(result.output)}</pre>` : ""}
      </article>
    `)
    .join("");
}

async function initAdminPage() {
  const problemForm = document.getElementById("problem-create-form");
  const testCaseForm = document.getElementById("test-case-form");
  const refreshUsers = document.getElementById("refresh-users");
  if (problemForm) {
    problemForm.addEventListener("submit", handleProblemCreate);
  }
  if (testCaseForm) {
    testCaseForm.addEventListener("submit", handleTestCaseCreate);
  }
  if (refreshUsers) {
    refreshUsers.addEventListener("click", loadAdminUsers);
  }
  renderAdminGate();
  if (state.user?.role === "admin") {
    await loadAdminUsers();
  }
}

function renderAdminGate() {
  const gate = document.getElementById("admin-gate-message");
  if (!gate) {
    return;
  }
  if (state.user?.role === "admin") {
    setFeedback(gate, t("adminPage.accessGranted"), "success");
    setAdminFormsDisabled(false);
  } else {
    setFeedback(gate, t("adminPage.accessDenied"), "error");
    setAdminFormsDisabled(true);
  }
}

function setAdminFormsDisabled(disabled) {
  ["problem-create-form", "test-case-form"].forEach((id) => {
    const form = document.getElementById(id);
    if (!form) {
      return;
    }
    form.querySelectorAll("input, textarea, select, button").forEach((node) => {
      node.disabled = disabled;
    });
  });
  const refreshUsers = document.getElementById("refresh-users");
  if (refreshUsers) {
    refreshUsers.disabled = disabled;
  }
}

async function handleProblemCreate(event) {
  event.preventDefault();
  const feedback = document.getElementById("problem-create-feedback");
  try {
    const payload = formToJson(event.currentTarget);
    payload.is_public = Boolean(payload.is_public);
    const created = await apiFetch("/api/v1/problems", {
      method: "POST",
      body: JSON.stringify(payload),
    }, true);
    setFeedback(feedback, t("adminPage.createProblemSuccess", { slug: created.slug }), "success");
    event.currentTarget.reset();
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function handleTestCaseCreate(event) {
  event.preventDefault();
  const feedback = document.getElementById("test-case-feedback");
  try {
    const payload = formToJson(event.currentTarget);
    const slug = payload.problem_slug;
    const request = {
      input: payload.input,
      expected_output: payload.expected_output,
      is_sample: Boolean(payload.is_sample),
      order: Number(payload.order || 0),
    };
    await apiFetch(`/api/v1/problems/${encodeURIComponent(slug)}/test-cases`, {
      method: "POST",
      body: JSON.stringify(request),
    }, true);
    setFeedback(feedback, t("adminPage.createTestCaseSuccess", { slug }), "success");
    event.currentTarget.reset();
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function loadAdminUsers() {
  if (state.user?.role !== "admin") {
    renderAdminUsers();
    return;
  }
  try {
    const response = await apiFetch("/api/v1/admin/users?page=1&page_size=50", {}, true);
    state.adminUsers = response.items || [];
  } catch {
    state.adminUsers = [];
  }
  renderAdminUsers();
}

function renderAdminUsers() {
  const list = document.getElementById("admin-user-list");
  if (!list) {
    return;
  }
  if (state.user?.role !== "admin") {
    list.innerHTML = `<div class="empty-state">${escapeHtml(t("adminPage.accessDenied"))}</div>`;
    return;
  }
  const users = state.adminUsers || [];
  if (!users.length) {
    list.innerHTML = `<div class="empty-state">${escapeHtml(t("adminPage.noUsers"))}</div>`;
    return;
  }
  list.innerHTML = users.map((user) => `
    <article class="user-card" data-user-id="${escapeHtml(user.id)}">
      <strong>${escapeHtml(user.username)}</strong>
      <p>${escapeHtml(user.email)}</p>
      <div class="meta-row">
        <span class="status-chip neutral">${escapeHtml(translateRole(user.role))}</span>
      </div>
      <div class="user-actions">
        <select data-role-select>
          <option value="user" ${user.role === "user" ? "selected" : ""}>${escapeHtml(t("session.roleUser"))}</option>
          <option value="admin" ${user.role === "admin" ? "selected" : ""}>${escapeHtml(t("session.roleAdmin"))}</option>
        </select>
        <button class="secondary-button compact" type="button" data-change-role>${escapeHtml(t("adminPage.changeRole"))}</button>
      </div>
    </article>
  `).join("");
  list.querySelectorAll("[data-change-role]").forEach((button) => {
    button.addEventListener("click", async () => {
      const card = button.closest("[data-user-id]");
      const userId = card?.getAttribute("data-user-id");
      const role = card?.querySelector("[data-role-select]")?.value;
      await changeUserRole(userId, role);
    });
  });
}

async function changeUserRole(userId, role) {
  const feedback = document.getElementById("admin-user-feedback");
  try {
    const updated = await apiFetch(`/api/v1/admin/users/${userId}/role?role=${encodeURIComponent(role)}`, {
      method: "PATCH",
    }, true);
    setFeedback(feedback, t("adminPage.roleUpdated", { username: updated.username }), "success");
    await loadAdminUsers();
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function apiFetch(path, options = {}, authenticated = false) {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if ((authenticated || state.token) && state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }
  const response = await fetch(path, { ...options, headers });
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof payload === "string" ? payload : payload.detail || "Request failed";
    throw new Error(message);
  }
  return payload;
}

function renderProblemCard(problem) {
  const localized = localizeProblem(problem);
  return `
    <a class="problem-card" href="/problem?slug=${encodeURIComponent(problem.slug)}" data-problem-link>
      <strong>${escapeHtml(localized.title)}</strong>
      <p>${escapeHtml(problem.slug)}</p>
      <div class="meta-row">
        <span class="status-chip ${difficultyClass(problem.difficulty)}">${escapeHtml(translateDifficulty(problem.difficulty))}</span>
        <span class="status-chip neutral">${escapeHtml(problem.is_public ? t("visibility.public") : t("visibility.private"))}</span>
      </div>
    </a>
  `;
}

function renderSubmissionCard(submission) {
  const active = state.selectedSubmission && state.selectedSubmission.id === submission.id;
  const problemTitle = localizeProblemTitle(submission.problem_slug, submission.problem_title || submission.problem_slug);
  return `
    <button class="submission-card ${active ? "active" : ""}" type="button" data-submission-id="${escapeHtml(submission.id)}">
      <strong>${escapeHtml(problemTitle)}</strong>
      <p>${escapeHtml(submission.problem_slug || "")}</p>
      <div class="meta-row">
        <span class="status-chip ${statusClass(submission.status)}">${escapeHtml(translateStatus(submission.status))}</span>
        <span class="status-chip neutral">${escapeHtml(t("common.passed", { passed: submission.passed_test_cases, total: submission.total_test_cases }))}</span>
        <span class="status-chip neutral">${escapeHtml(t("common.ms", { value: Math.round(submission.max_execution_time_ms || 0) }))}</span>
      </div>
    </button>
  `;
}

function bindProblemCardLinks(root) {
  root.querySelectorAll("[data-problem-link]").forEach((link) => {
    link.addEventListener("click", () => {
      stopPolling();
    });
  });
}

function startListPolling(callback) {
  stopPolling();
  state.pollTimer = window.setInterval(callback, 3000);
}

function stopPolling() {
  if (state.pollTimer) {
    clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
}

function persistSession(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem("oj_token", token);
  localStorage.setItem("oj_user", JSON.stringify(user));
}

function logout() {
  localStorage.removeItem("oj_token");
  localStorage.removeItem("oj_user");
  state.token = "";
  state.user = null;
  stopPolling();
  syncHeader();
  window.location.reload();
}

function localizeProblem(problem) {
  if (!problem) {
    return problem;
  }
  const translated = DEMO_PROBLEM_TRANSLATIONS[state.language]?.[problem.slug];
  return translated ? { ...problem, ...translated } : problem;
}

function localizeProblemTitle(slug, fallbackTitle) {
  const translated = DEMO_PROBLEM_TRANSLATIONS[state.language]?.[slug];
  return translated?.title || fallbackTitle || slug;
}

function translateDifficulty(difficulty) {
  return t(`difficulty.${difficulty}`);
}

function translateStatus(status) {
  return t(`status.${status}`) || status;
}

function translateRole(role) {
  return role === "admin" ? t("session.roleAdmin") : t("session.roleUser");
}

function difficultyClass(difficulty) {
  if (difficulty === "easy") {
    return "success";
  }
  if (difficulty === "medium") {
    return "warning";
  }
  return "danger";
}

function statusClass(status) {
  if (status === "accepted") {
    return "success";
  }
  if (status === "pending" || status === "running") {
    return "running";
  }
  if (status === "wrong_answer" || status === "time_limit_exceeded") {
    return "warning";
  }
  return "danger";
}

function t(key, vars = {}) {
  const current = lookupTranslation(state.language, key);
  const fallback = lookupTranslation("en", key);
  const template = current || fallback || key;
  return template.replace(/\{(\w+)\}/g, (_, token) => (token in vars ? String(vars[token]) : `{${token}}`));
}

function lookupTranslation(locale, key) {
  return key.split(".").reduce((value, part) => (value && value[part] !== undefined ? value[part] : null), translations[locale]);
}

function formToJson(form) {
  const formData = new FormData(form);
  const payload = {};
  formData.forEach((value, key) => {
    if (payload[key] !== undefined) {
      return;
    }
    const field = form.querySelector(`[name="${CSS.escape(key)}"]`);
    if (field?.type === "checkbox") {
      payload[key] = field.checked;
    } else {
      payload[key] = value;
    }
  });
  form.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    if (!(checkbox.name in payload)) {
      payload[checkbox.name] = checkbox.checked;
    }
  });
  return payload;
}

function setFeedback(node, message, kind = "") {
  if (!node) {
    return;
  }
  node.textContent = message;
  node.className = "feedback";
  if (kind) {
    node.classList.add(kind);
  }
}

function detectLanguage() {
  const candidates = Array.isArray(navigator.languages) && navigator.languages.length
    ? navigator.languages
    : [navigator.language || DEFAULT_LANGUAGE];
  for (const candidate of candidates) {
    const resolved = resolveLanguage(candidate);
    if (resolved) {
      return resolved;
    }
  }
  return DEFAULT_LANGUAGE;
}

function resolveLanguage(value) {
  if (!value) {
    return DEFAULT_LANGUAGE;
  }
  if (value === "zh-CN" || value === "en") {
    return value;
  }
  const normalized = value.toLowerCase();
  if (LANGUAGE_ALIASES[normalized]) {
    return LANGUAGE_ALIASES[normalized];
  }
  const base = normalized.split("-")[0];
  if (LANGUAGE_ALIASES[base]) {
    return LANGUAGE_ALIASES[base];
  }
  return DEFAULT_LANGUAGE;
}

function loadStoredJson(key) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function debounce(fn, delayMs) {
  let timerId = null;
  return (...args) => {
    if (timerId) {
      clearTimeout(timerId);
    }
    timerId = window.setTimeout(() => fn(...args), delayMs);
  };
}

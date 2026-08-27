import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const structurePath = path.join(__dirname, "01_guide_structure.json");
const outputPath = path.join(__dirname, "coding-workbook.xlsx");
const renderDir = path.join(__dirname, "renders");
const inspectPath = path.join(__dirname, "03_verification_summary.json");

const structure = JSON.parse(await fs.readFile(structurePath, "utf8"));

const reservedRows = structure.reserved_participant_rows ?? 20;
const participantFields = structure.participant_fields ?? [
  "PID",
  "이름/익명",
  "성별",
  "연령",
  "세션그룹",
  "인터뷰일시",
  "투자성향",
  "사전설문 메모",
  "코딩 메모",
];

const q45Items = structure?.q45_scale?.items?.length
  ? structure.q45_scale.items
  : [
      "1. (간편설계의) 쉽고 간편한 설계",
      "2. (상세설계의) 상세한 설계",
      "3. 상세설계의 입력값 추천과 도움말",
      "4. 다른 금융사 연금 가져오기",
      "5. 다른 금융사와 합산하여 연금 계획 세우기",
      "6. 목표 (수정) 제안",
      "7. 포트폴리오 구성",
      "8. 맞춤 상품 추천",
      "9. 리밸런싱",
      "10. 설계 내역",
      "11. 투자수익률 알림",
    ];

const q47Items = structure?.q47_sus?.items?.length
  ? structure.q47_sus.items
  : [
      "나는 이 서비스를 자주 사용할 것 같다",
      "나는 이 서비스가 불필요하게 복잡하다고 느꼈다",
      "나는 이 서비스는 사용하기 편리하다고 느꼈다",
      "내가 이 서비스를 사용하기 위해선 기술적 도움이 필요할 것 같다고 느꼈다",
      "나는 이 서비스에는 다양한 기능이 잘 통합되어있다고 생각했다",
      "나는 이 서비스에 일관적이지 않은 부분이 너무 많다고 느꼈다",
      "나는 대부분의 사람들이 이 서비스를 사용하는 방법을 쉽게 배울 것이라고 생각한다",
      "나는 이 서비스는 사용하기 불편하고 어색하다고 느꼈다",
      "나는 이 서비스를 사용하는 것에 자신감을 느꼈다",
      "이 서비스를 사용하기 전에 많은 것을 배워야 할 것 같다고 느꼈다",
    ];

const recognitionItems = structure?.recognition_usefulness?.length
  ? structure.recognition_usefulness
  : [
      { question_no: 15, screen: "목표 진단", prompt: "목표를 수정할까요?" },
      { question_no: 19, screen: "상세 포트폴리오", prompt: "상세 포트폴리오 보기" },
      { question_no: 20, screen: "ETF 추천 상품", prompt: "ETF 상품도 있어요!" },
      { question_no: 23, screen: "설계 결과", prompt: "투자는 교체 매매로 진행돼요!" },
      { question_no: 40, screen: "서비스 소개", prompt: "설계 내역" },
      { question_no: 41, screen: "설계내역", prompt: "투자수익률알림설정하기" },
      { question_no: 42, screen: "설계내역", prompt: "스마트연금케어시작하기" },
    ];

const preferenceItems = structure?.preference_questions?.length
  ? structure.preference_questions
  : [
      {
        question_no: 32,
        prompt: "간편설계 vs 상세설계 중 더 선호하는 방식과 이유",
      },
      {
        question_no: 44,
        prompt: "설계내역 vs 타 앱 관리 방식 중 더 선호하는 방식과 이유",
      },
      {
        question_no: 49,
        prompt: "숫자 vs 이미지 표현 방식 중 더 선호하는 방식과 이유",
      },
    ];

const openBattery = structure?.open_response_battery?.length
  ? structure.open_response_battery
  : [
      { question_no: 2, screen: "서비스 소개", prompt: "가장 기억에 남는 키워드 3개는?" },
      { question_no: 3, screen: "설계 방식 선택", prompt: "두 가지 방식의 차이는 무엇 같나요?" },
      { question_no: 4, screen: "상세설계", prompt: "어떤 버튼을 눌렀을 것 같나요?" },
      { question_no: 5, screen: "목표 진단", prompt: "가장 기억에 남는 정보는 무엇이었나요?" },
      { question_no: 6, screen: "AI 컨설팅", prompt: "어떤 화면으로 이해했나요?" },
      { question_no: 7, screen: "설계 결과", prompt: "다음 단계는 무엇이라고 생각하나요?" },
    ];

const adjectiveGroups = structure?.adjective_card?.groups ?? {
  긍정: [
    "흥미진진한",
    "편리한",
    "친절한",
    "차분한",
    "사용하기 쉬운",
    "재미있는",
    "직관적인",
    "세련된",
    "인상적인",
    "전문적인",
    "고급스러운",
    "신뢰할 수 있는",
    "간결한",
    "유용한",
  ],
  중립: ["일관된", "명확한", "단순한", "익숙한", "최신의"],
  부정: [
    "지루한",
    "일관성 없는",
    "산만한",
    "혼란스러운",
    "사용하기 어려운",
    "딱딱한",
    "복잡한",
    "세련되지 않은",
    "평범한",
    "품질이 낮은",
  ],
};

const targetedQuestions = new Set([
  ...openBattery.map((item) => item.question_no),
  8,
  ...recognitionItems.map((item) => item.question_no),
  ...preferenceItems.map((item) => item.question_no),
  45,
  47,
]);

const noteRows = (structure.note_rows ?? []).filter((row) => {
  const value = Number(row.question_no);
  return Number.isFinite(value) && targetedQuestions.has(value);
});

const COLORS = {
  header: "#0F766E",
  headerText: "#FFFFFF",
  subHeader: "#D9F99D",
  paleBlue: "#DBEAFE",
  palePurple: "#EDE9FE",
  paleAmber: "#FEF3C7",
  paleGreen: "#DCFCE7",
  paleGray: "#F3F4F6",
  border: "#D1D5DB",
  text: "#111827",
  muted: "#6B7280",
};

function columnLetter(index) {
  let current = index;
  let result = "";
  while (current > 0) {
    const remainder = (current - 1) % 26;
    result = String.fromCharCode(65 + remainder) + result;
    current = Math.floor((current - 1) / 26);
  }
  return result;
}

function repeatedFormulaMatrix(formulas) {
  return formulas.map((formula) => [formula]);
}

function repeatedNullMatrix(rows, cols) {
  return Array.from({ length: rows }, () => Array.from({ length: cols }, () => null));
}

function repeatedValueMatrix(rows, cols, value = null) {
  return Array.from({ length: rows }, () => Array.from({ length: cols }, () => value));
}

function writeMergedTitle(sheet, title, lastColLetter) {
  const range = sheet.getRange(`A1:${lastColLetter}1`);
  range.merge();
  range.values = [[title]];
  range.format = {
    fill: COLORS.header,
    font: { bold: true, color: COLORS.headerText, size: 15 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: COLORS.header },
  };
  range.format.rowHeight = 28;
}

function writeNoteBand(sheet, text, lastColLetter) {
  const range = sheet.getRange(`A2:${lastColLetter}2`);
  range.merge();
  range.values = [[text]];
  range.format = {
    fill: COLORS.paleGray,
    font: { color: COLORS.text, italic: true },
    horizontalAlignment: "left",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.border },
  };
  range.format.rowHeight = 34;
}

function styleHeader(range, fill = COLORS.header, fontColor = COLORS.headerText) {
  range.format = {
    fill,
    font: { bold: true, color: fontColor },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.border },
  };
}

function styleBody(range, horizontalAlignment = "left") {
  range.format = {
    font: { color: COLORS.text },
    horizontalAlignment,
    verticalAlignment: "top",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.border },
  };
}

function setColumnWidths(sheet, widthPairs) {
  for (const [col, width] of widthPairs) {
    sheet.getRange(`${col}:${col}`).format.columnWidth = width;
  }
}

function participantIdFormulas(metaStartRow) {
  return Array.from({ length: reservedRows }, (_, index) => [
    `='01. 참여자 메타'!A${metaStartRow + index}`,
  ]);
}

function sanitizeFileName(value) {
  return value.replace(/[<>:"/\\|?*]+/g, "_");
}

const workbook = Workbook.create();
const orderedSheetNames = [
  "00. 노트테이킹",
  "01. 참여자 메타",
  "02. 주관식_10초테스트_Q2-Q7",
  "03. 객관식-형용사카드_Q8",
  "04. 인지와 유용_Q15-Q42",
  "05. 선호_코딩_Q32_Q44_Q49",
  "06. 객관식-5점척도_Q45",
  "07. 객관식-7점척도_Q47_SUS",
];

const sheets = Object.fromEntries(
  orderedSheetNames.map((name) => {
    const sheet = workbook.worksheets.add(name);
    sheet.showGridLines = false;
    return [name, sheet];
  }),
);

buildNotesSheet();
buildMetaSheet();
buildOpenBatterySheet();
buildAdjectiveSheet();
buildRecognitionSheet();
buildPreferenceSheet();
buildQ45Sheet();
buildQ47Sheet();

await fs.mkdir(renderDir, { recursive: true });

const renderFiles = [];
for (const sheetName of orderedSheetNames) {
  const blob = await workbook.render({
    sheetName,
    autoCrop: "all",
    scale: 1,
    format: "png",
  });
  const fileName = `${String(renderFiles.length + 1).padStart(2, "0")}_${sanitizeFileName(sheetName)}.png`;
  const filePath = path.join(renderDir, fileName);
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
  renderFiles.push(filePath);
}

const q45Sheet = sheets["06. 객관식-5점척도_Q45"];
const q47Sheet = sheets["07. 객관식-7점척도_Q47_SUS"];

const verificationSummary = {
  source_path: structure.source_path,
  guide_name: structure.guide_name,
  generated_at: new Date().toISOString(),
  fallback_usage: {
    q45_items_from_fallback: !structure?.q45_scale?.items?.length,
    q47_items_from_fallback: !structure?.q47_sus?.items?.length,
  },
  render_files: renderFiles,
  sheet_inspect: await workbook.inspect({
    kind: "sheet",
    include: "id,name",
    maxChars: 4000,
  }),
  q45_formula_snapshot: q45Sheet.getRange(`M5:N${4 + reservedRows}`).displayFormulas,
  q47_formula_snapshot: q47Sheet.getRange(`L5:M${4 + reservedRows}`).displayFormulas,
};

await fs.writeFile(inspectPath, JSON.stringify(verificationSummary, null, 2), "utf8");

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);

function buildNotesSheet() {
  const sheet = sheets["00. 노트테이킹"];
  const lastCol = "H";
  writeMergedTitle(sheet, "00. 노트테이킹", lastCol);
  writeNoteBand(
    sheet,
    "실제 세션 중 관찰/직접 인용/후속 탐침을 빠르게 적을 수 있도록 질문 단위 메모 행을 미리 배치했습니다.",
    lastCol,
  );

  sheet.getRange("A4:H4").values = [[
    "Stage",
    "Screen",
    "Activity Type",
    "Q#",
    "Prompt",
    "Observation / Behavior",
    "Key Quote",
    "Follow-up / Coding Memo",
  ]];
  styleHeader(sheet.getRange("A4:H4"));

  const body = noteRows.map((row) => [
    row.stage || "",
    row.screen || "",
    row.activity_type || "",
    row.question_no || "",
    row.prompt || row.content || "",
    null,
    null,
    null,
  ]);
  if (body.length > 0) {
    sheet.getRange(`A5:H${4 + body.length}`).values = body;
    styleBody(sheet.getRange(`A5:H${4 + body.length}`));
  }

  setColumnWidths(sheet, [
    ["A", 18],
    ["B", 18],
    ["C", 18],
    ["D", 8],
    ["E", 55],
    ["F", 28],
    ["G", 28],
    ["H", 28],
  ]);
  sheet.freezePanes.freezeRows(4);
}

function buildMetaSheet() {
  const sheet = sheets["01. 참여자 메타"];
  const headers = [...participantFields, "완료여부"];
  const lastCol = columnLetter(headers.length);
  writeMergedTitle(sheet, "01. 참여자 메타", lastCol);
  writeNoteBand(
    sheet,
    "참여자 메타는 다른 시트의 PID 기준값으로 연결됩니다. 이름 대신 익명 ID만 써도 됩니다.",
    lastCol,
  );

  sheet.getRange(`A4:${lastCol}4`).values = [headers];
  styleHeader(sheet.getRange(`A4:${lastCol}4`));

  sheet.getRange(`A5:A${4 + reservedRows}`).formulas = repeatedFormulaMatrix(
    Array.from({ length: reservedRows }, (_, index) => `="P"&TEXT(ROW()-4,"00")`),
  );
  sheet.getRange(`B5:${columnLetter(headers.length - 1)}${4 + reservedRows}`).values = repeatedNullMatrix(
    reservedRows,
    headers.length - 2,
  );
  sheet.getRange(`J5:J${4 + reservedRows}`).values = repeatedNullMatrix(reservedRows, 1);

  styleBody(sheet.getRange(`A5:${lastCol}${4 + reservedRows}`));
  sheet.getRange(`J5:J${4 + reservedRows}`).dataValidation = {
    allowBlank: true,
    list: { inCellDropDown: true, source: ["미시작", "진행중", "완료"] },
  };

  setColumnWidths(sheet, [
    ["A", 10],
    ["B", 16],
    ["C", 10],
    ["D", 10],
    ["E", 14],
    ["F", 16],
    ["G", 12],
    ["H", 18],
    ["I", 18],
    ["J", 12],
  ]);

  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(1);
}

function buildOpenBatterySheet() {
  const sheet = sheets["02. 주관식_10초테스트_Q2-Q7"];
  const lastCol = columnLetter(openBattery.length + 2);
  writeMergedTitle(sheet, "02. 주관식_10초테스트_Q2-Q7", lastCol);
  writeNoteBand(
    sheet,
    "5초/10초 테스트형 짧은 자유응답을 한 행에 한 참여자씩 기록합니다. 마지막 열은 빠른 요약용입니다.",
    lastCol,
  );

  const headers = [
    "ID",
    ...openBattery.map(
      (item) => `Q${item.question_no}\n[${item.screen}]\n${item.prompt}`,
    ),
    "핵심 메모",
  ];
  sheet.getRange(`A4:${lastCol}4`).values = [headers];
  styleHeader(sheet.getRange(`A4:${lastCol}4`));
  sheet.getRange(`A4:${lastCol}4`).format.rowHeight = 88;

  sheet.getRange(`A5:A${4 + reservedRows}`).formulas = participantIdFormulas(5);
  sheet.getRange(`B5:${lastCol}${4 + reservedRows}`).values = repeatedNullMatrix(
    reservedRows,
    headers.length - 1,
  );
  styleBody(sheet.getRange(`A5:${lastCol}${4 + reservedRows}`));

  setColumnWidths(sheet, [
    ["A", 10],
    ["B", 26],
    ["C", 26],
    ["D", 26],
    ["E", 26],
    ["F", 26],
    ["G", 26],
    ["H", 20],
  ]);
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(1);
}

function buildAdjectiveSheet() {
  const sheet = sheets["03. 객관식-형용사카드_Q8"];
  const allLabels = Object.values(adjectiveGroups).flat();
  const lastCol = columnLetter(allLabels.length + 2);
  writeMergedTitle(sheet, "03. 객관식-형용사카드_Q8", lastCol);
  writeNoteBand(
    sheet,
    "참여자가 고른 형용사는 B열에 요약하고, 개별 카드 선택 여부는 TRUE/FALSE로 표시합니다. 6행은 빈도 확인용입니다.",
    lastCol,
  );

  sheet.getRange(`A4:B5`).values = [
    [null, null],
    ["ID", "선택 형용사(쉼표)"],
  ];
  styleHeader(sheet.getRange("A4:B5"), COLORS.paleGray, COLORS.text);

  let currentColumnIndex = 3;
  for (const [groupName, labels] of Object.entries(adjectiveGroups)) {
    const start = columnLetter(currentColumnIndex);
    const end = columnLetter(currentColumnIndex + labels.length - 1);
    const groupRange = sheet.getRange(`${start}4:${end}4`);
    groupRange.merge();
    groupRange.values = [[groupName]];
    styleHeader(
      groupRange,
      groupName === "긍정"
        ? COLORS.paleGreen
        : groupName === "중립"
          ? COLORS.paleBlue
          : COLORS.paleAmber,
      COLORS.text,
    );
    currentColumnIndex += labels.length;
  }

  sheet.getRange(`C5:${lastCol}5`).values = [allLabels];
  styleHeader(sheet.getRange(`C5:${lastCol}5`), COLORS.header, COLORS.headerText);
  sheet.getRange(`C5:${lastCol}5`).format.rowHeight = 56;

  sheet.getRange(`A6:B6`).values = [["count", "Q8 선택 빈도"]];
  styleHeader(sheet.getRange("A6:B6"), COLORS.paleGray, COLORS.text);
  sheet.getRange(`C6:${lastCol}6`).formulas = [
    allLabels.map((_, index) => {
      const col = columnLetter(index + 3);
      return `=COUNTIF(${col}7:${col}${6 + reservedRows},TRUE)`;
    }),
  ];
  styleHeader(sheet.getRange(`C6:${lastCol}6`), COLORS.paleGray, COLORS.text);

  sheet.getRange(`A7:A${6 + reservedRows}`).formulas = participantIdFormulas(5);
  sheet.getRange(`B7:${lastCol}${6 + reservedRows}`).values = repeatedNullMatrix(
    reservedRows,
    allLabels.length + 1,
  );
  styleBody(sheet.getRange(`A7:${lastCol}${6 + reservedRows}`), "center");
  sheet.getRange(`B7:B${6 + reservedRows}`).format.horizontalAlignment = "left";

  sheet.getRange(`C7:${lastCol}${6 + reservedRows}`).dataValidation = {
    allowBlank: true,
    list: { inCellDropDown: true, source: ["TRUE", "FALSE"] },
  };

  setColumnWidths(sheet, [
    ["A", 10],
    ["B", 26],
  ]);
  for (let index = 3; index <= allLabels.length + 2; index += 1) {
    sheet.getRange(`${columnLetter(index)}:${columnLetter(index)}`).format.columnWidth = 11;
  }
  sheet.freezePanes.freezeRows(6);
  sheet.freezePanes.freezeColumns(2);
}

function buildRecognitionSheet() {
  const sheet = sheets["04. 인지와 유용_Q15-Q42"];
  const totalColumns = 1 + recognitionItems.length * 2 + 1;
  const lastCol = columnLetter(totalColumns);
  writeMergedTitle(sheet, "04. 인지와 유용_Q15-Q42", lastCol);
  writeNoteBand(
    sheet,
    "각 질문마다 참여자가 내용을 ‘인지’했는지와 ‘유용’하다고 느꼈는지를 TRUE/FALSE로 기록합니다. 마지막 열은 메모용입니다.",
    lastCol,
  );

  const row4 = ["질문번호"];
  const row5 = ["질문 내용/스크린"];
  const row6 = ["ID"];
  for (const item of recognitionItems) {
    row4.push(item.question_no, item.question_no);
    row5.push(item.screen || item.prompt || "", item.screen || item.prompt || "");
    row6.push("인지", "유용");
  }
  row4.push(null);
  row5.push(null);
  row6.push("종합 메모");

  sheet.getRange(`A4:${lastCol}4`).values = [row4];
  sheet.getRange(`A5:${lastCol}5`).values = [row5];
  sheet.getRange(`A6:${lastCol}6`).values = [row6];
  styleHeader(sheet.getRange(`A4:${lastCol}4`), COLORS.palePurple, COLORS.text);
  styleHeader(sheet.getRange(`A5:${lastCol}5`), COLORS.paleBlue, COLORS.text);
  styleHeader(sheet.getRange(`A6:${lastCol}6`), COLORS.header, COLORS.headerText);
  sheet.getRange(`A5:${lastCol}5`).format.rowHeight = 48;

  sheet.getRange(`A7:A${6 + reservedRows}`).formulas = participantIdFormulas(5);
  sheet.getRange(`B7:${lastCol}${6 + reservedRows}`).values = repeatedNullMatrix(
    reservedRows,
    totalColumns - 1,
  );
  styleBody(sheet.getRange(`A7:${lastCol}${6 + reservedRows}`), "center");
  sheet.getRange(`${columnLetter(totalColumns)}7:${lastCol}${6 + reservedRows}`).format.horizontalAlignment =
    "left";

  const booleanLastCol = columnLetter(totalColumns - 1);
  sheet.getRange(`B7:${booleanLastCol}${6 + reservedRows}`).dataValidation = {
    allowBlank: true,
    list: { inCellDropDown: true, source: ["TRUE", "FALSE"] },
  };

  const countRow = 7 + reservedRows;
  sheet.getRange(`A${countRow}:${lastCol}${countRow}`).values = [
    [
      "count_TRUE",
      ...Array.from({ length: recognitionItems.length * 2 }, (_, index) => {
        const col = columnLetter(index + 2);
        return `=COUNTIF(${col}7:${col}${6 + reservedRows},TRUE)`;
      }),
      null,
    ],
  ];
  // replace string formulas with real formulas in B:...
  sheet.getRange(`B${countRow}:${booleanLastCol}${countRow}`).formulas = [
    Array.from({ length: recognitionItems.length * 2 }, (_, index) => {
      const col = columnLetter(index + 2);
      return `=COUNTIF(${col}7:${col}${6 + reservedRows},TRUE)`;
    }),
  ];
  styleHeader(sheet.getRange(`A${countRow}:${lastCol}${countRow}`), COLORS.paleGray, COLORS.text);

  setColumnWidths(sheet, [["A", 10]]);
  for (let index = 2; index <= totalColumns - 1; index += 1) {
    sheet.getRange(`${columnLetter(index)}:${columnLetter(index)}`).format.columnWidth =
      index % 2 === 0 ? 12 : 12;
  }
  sheet.getRange(`${lastCol}:${lastCol}`).format.columnWidth = 20;
  sheet.freezePanes.freezeRows(6);
  sheet.freezePanes.freezeColumns(1);
}

function buildPreferenceSheet() {
  const sheet = sheets["05. 선호_코딩_Q32_Q44_Q49"];
  const lastCol = "H";
  writeMergedTitle(sheet, "05. 선호_코딩_Q32_Q44_Q49", lastCol);
  writeNoteBand(
    sheet,
    "선호 선택과 이유를 함께 남길 수 있게 설계했습니다. 드롭다운 값은 실제 코딩 시 필요하면 더 좁히거나 늘릴 수 있습니다.",
    lastCol,
  );

  const headerPrompts = [
    null,
    preferenceItems[0]?.prompt ?? "",
    preferenceItems[0]?.prompt ?? "",
    preferenceItems[1]?.prompt ?? "",
    preferenceItems[1]?.prompt ?? "",
    preferenceItems[2]?.prompt ?? "",
    preferenceItems[2]?.prompt ?? "",
    null,
  ];
  const headers = [
    "ID",
    "Q32 선택",
    "Q32 이유 요약",
    "Q44 선택",
    "Q44 이유 요약",
    "Q49 선택",
    "Q49 이유 요약",
    "종합 메모",
  ];

  sheet.getRange("A4:H4").values = [headerPrompts];
  sheet.getRange("A5:H5").values = [headers];
  styleHeader(sheet.getRange("A4:H4"), COLORS.paleBlue, COLORS.text);
  styleHeader(sheet.getRange("A5:H5"));
  sheet.getRange("A4:H4").format.rowHeight = 60;

  sheet.getRange(`A6:A${5 + reservedRows}`).formulas = participantIdFormulas(5);
  sheet.getRange(`B6:H${5 + reservedRows}`).values = repeatedNullMatrix(reservedRows, 7);
  styleBody(sheet.getRange(`A6:H${5 + reservedRows}`));
  sheet.getRange(`A6:A${5 + reservedRows}`).format.horizontalAlignment = "center";

  sheet.getRange(`B6:B${5 + reservedRows}`).dataValidation = {
    allowBlank: true,
    list: { inCellDropDown: true, source: ["간편설계", "상세설계", "둘 다/기타"] },
  };
  sheet.getRange(`D6:D${5 + reservedRows}`).dataValidation = {
    allowBlank: true,
    list: { inCellDropDown: true, source: ["설계내역", "타 앱 관리", "둘 다/기타"] },
  };
  sheet.getRange(`F6:F${5 + reservedRows}`).dataValidation = {
    allowBlank: true,
    list: { inCellDropDown: true, source: ["숫자", "이미지", "둘 다/기타"] },
  };

  setColumnWidths(sheet, [
    ["A", 10],
    ["B", 14],
    ["C", 22],
    ["D", 14],
    ["E", 22],
    ["F", 14],
    ["G", 22],
    ["H", 22],
  ]);
  sheet.freezePanes.freezeRows(5);
  sheet.freezePanes.freezeColumns(1);
}

function buildQ45Sheet() {
  const sheet = sheets["06. 객관식-5점척도_Q45"];
  const totalColumns = 1 + q45Items.length + 2;
  const lastCol = columnLetter(totalColumns);
  writeMergedTitle(sheet, "06. 객관식-5점척도_Q45", lastCol);
  writeNoteBand(
    sheet,
    "1~5점 응답을 참여자별 행 기준으로 입력합니다. 마지막 두 열은 평균과 응답 개수를 자동 계산합니다.",
    lastCol,
  );

  const headers = ["ID", ...q45Items, "평균", "응답 개수"];
  sheet.getRange(`A4:${lastCol}4`).values = [headers];
  styleHeader(sheet.getRange(`A4:${lastCol}4`));
  sheet.getRange(`A4:${lastCol}4`).format.rowHeight = 72;

  sheet.getRange(`A5:A${4 + reservedRows}`).formulas = participantIdFormulas(5);
  sheet.getRange(`B5:${columnLetter(1 + q45Items.length)}${4 + reservedRows}`).values =
    repeatedNullMatrix(reservedRows, q45Items.length);
  sheet.getRange(`M5:M${4 + reservedRows}`).formulas = repeatedFormulaMatrix(
    Array.from(
      { length: reservedRows },
      (_, index) => `=IF(COUNTA(B${5 + index}:L${5 + index})=0,"",ROUND(AVERAGE(B${5 + index}:L${5 + index}),2))`,
    ),
  );
  sheet.getRange(`N5:N${4 + reservedRows}`).formulas = repeatedFormulaMatrix(
    Array.from({ length: reservedRows }, (_, index) => `=COUNT(B${5 + index}:L${5 + index})`),
  );

  styleBody(sheet.getRange(`A5:${lastCol}${4 + reservedRows}`), "center");
  sheet.getRange(`B5:L${4 + reservedRows}`).dataValidation = {
    allowBlank: true,
    rule: { type: "whole", operator: "between", formula1: 1, formula2: 5 },
    errorAlert: {
      style: "stop",
      title: "점수 범위 오류",
      message: "1점부터 5점 사이의 정수만 입력하세요.",
    },
  };

  const summaryCountRow = 5 + reservedRows;
  const summaryMeanRow = 6 + reservedRows;
  sheet.getRange(`A${summaryCountRow}:A${summaryMeanRow}`).values = [["응답수"], ["항목 평균"]];
  sheet.getRange(`B${summaryCountRow}:L${summaryCountRow}`).formulas = [
    q45Items.map((_, index) => {
      const col = columnLetter(index + 2);
      return `=COUNT(${col}5:${col}${4 + reservedRows})`;
    }),
  ];
  sheet.getRange(`B${summaryMeanRow}:L${summaryMeanRow}`).formulas = [
    q45Items.map((_, index) => {
      const col = columnLetter(index + 2);
      return `=IF(COUNT(${col}5:${col}${4 + reservedRows})=0,"",ROUND(AVERAGE(${col}5:${col}${4 + reservedRows}),2))`;
    }),
  ];
  styleHeader(
    sheet.getRange(`A${summaryCountRow}:${lastCol}${summaryMeanRow}`),
    COLORS.paleGray,
    COLORS.text,
  );

  setColumnWidths(sheet, [["A", 10]]);
  for (let index = 2; index <= 12; index += 1) {
    sheet.getRange(`${columnLetter(index)}:${columnLetter(index)}`).format.columnWidth = 16;
  }
  sheet.getRange("M:M").format.columnWidth = 10;
  sheet.getRange("N:N").format.columnWidth = 10;
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(1);
}

function buildQ47Sheet() {
  const sheet = sheets["07. 객관식-7점척도_Q47_SUS"];
  const totalColumns = 1 + q47Items.length + 3;
  const lastCol = columnLetter(totalColumns);
  writeMergedTitle(sheet, "07. 객관식-7점척도_Q47_SUS", lastCol);
  writeNoteBand(
    sheet,
    "1~7점 응답을 입력하면 SUS 점수(100점 만점)와 Grade를 자동 계산합니다. 홀수 문항은 정방향, 짝수 문항은 역방향으로 계산합니다.",
    lastCol,
  );

  const headers = ["ID", ...q47Items.map((item, index) => `Q${index + 1}\n${item}`), "SUS 점수", "SUS Grade", "비고"];
  sheet.getRange(`A4:${lastCol}4`).values = [headers];
  styleHeader(sheet.getRange(`A4:${lastCol}4`));
  sheet.getRange(`A4:${lastCol}4`).format.rowHeight = 96;

  sheet.getRange(`A5:A${4 + reservedRows}`).formulas = participantIdFormulas(5);
  sheet.getRange(`B5:K${4 + reservedRows}`).values = repeatedNullMatrix(reservedRows, q47Items.length);
  sheet.getRange(`L5:L${4 + reservedRows}`).formulas = repeatedFormulaMatrix(
    Array.from(
      { length: reservedRows },
      (_, index) =>
        `=IF(COUNTA(B${5 + index}:K${5 + index})=0,"",((B${5 + index}-1)+(7-C${5 + index})+(D${5 + index}-1)+(7-E${5 + index})+(F${5 + index}-1)+(7-G${5 + index})+(H${5 + index}-1)+(7-I${5 + index})+(J${5 + index}-1)+(7-K${5 + index}))*2.5)`,
    ),
  );
  sheet.getRange(`M5:M${4 + reservedRows}`).formulas = repeatedFormulaMatrix(
    Array.from(
      { length: reservedRows },
      (_, index) =>
        `=IF(L${5 + index}="","",IF(L${5 + index}>=80.3,"A",IF(L${5 + index}>=68,"B",IF(L${5 + index}>=51,"C",IF(L${5 + index}>=38,"D","F")))))`,
    ),
  );
  sheet.getRange(`N5:N${4 + reservedRows}`).values = repeatedValueMatrix(reservedRows, 1, null);

  styleBody(sheet.getRange(`A5:${lastCol}${4 + reservedRows}`), "center");
  sheet.getRange(`B5:K${4 + reservedRows}`).dataValidation = {
    allowBlank: true,
    rule: { type: "whole", operator: "between", formula1: 1, formula2: 7 },
    errorAlert: {
      style: "stop",
      title: "점수 범위 오류",
      message: "1점부터 7점 사이의 정수만 입력하세요.",
    },
  };
  sheet.getRange(`N5:N${4 + reservedRows}`).format.horizontalAlignment = "left";

  const summaryCountRow = 5 + reservedRows;
  const summaryMeanRow = 6 + reservedRows;
  sheet.getRange(`A${summaryCountRow}:A${summaryMeanRow}`).values = [["응답수"], ["항목 평균"]];
  sheet.getRange(`B${summaryCountRow}:K${summaryCountRow}`).formulas = [
    q47Items.map((_, index) => {
      const col = columnLetter(index + 2);
      return `=COUNT(${col}5:${col}${4 + reservedRows})`;
    }),
  ];
  sheet.getRange(`B${summaryMeanRow}:K${summaryMeanRow}`).formulas = [
    q47Items.map((_, index) => {
      const col = columnLetter(index + 2);
      return `=IF(COUNT(${col}5:${col}${4 + reservedRows})=0,"",ROUND(AVERAGE(${col}5:${col}${4 + reservedRows}),2))`;
    }),
  ];
  sheet.getRange(`L${summaryCountRow}:L${summaryMeanRow}`).formulas = [[`=COUNT(L5:L${4 + reservedRows})`], [`=IF(COUNT(L5:L${4 + reservedRows})=0,"",ROUND(AVERAGE(L5:L${4 + reservedRows}),2))`]];
  styleHeader(
    sheet.getRange(`A${summaryCountRow}:${lastCol}${summaryMeanRow}`),
    COLORS.paleGray,
    COLORS.text,
  );

  setColumnWidths(sheet, [["A", 10]]);
  for (let index = 2; index <= 11; index += 1) {
    sheet.getRange(`${columnLetter(index)}:${columnLetter(index)}`).format.columnWidth = 16;
  }
  sheet.getRange("L:L").format.columnWidth = 12;
  sheet.getRange("M:M").format.columnWidth = 12;
  sheet.getRange("N:N").format.columnWidth = 18;
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(1);
}

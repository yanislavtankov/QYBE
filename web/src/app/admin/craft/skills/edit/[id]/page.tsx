import SkillEditorPage from "@/views/SkillEditorPage";

export interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function AdminEditSkillPage({ params }: PageProps) {
  const { id } = await params;
  return <SkillEditorPage skillId={id} />;
}

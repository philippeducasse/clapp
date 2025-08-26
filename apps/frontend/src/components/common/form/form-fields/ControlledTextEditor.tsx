import { ControllerRenderProps } from "react-hook-form";
import { FormItem } from "@/components/ui/form";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { Bold, Italic, List, ListOrdered, Strikethrough, Minus, Redo, Undo } from "lucide-react";
import { Toggle } from "@/components/ui/toggle";

interface ControlledTextEditorProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
}

export const ControlledTextEditor = ({ field }: ControlledTextEditorProps) => {
  const editor = useEditor({
    extensions: [StarterKit],
    immediatelyRender: false,
    content: field,
    onUpdate: ({ editor }) => {
      field.onChange(editor.getHTML());
    },
  });

  return (
    <FormItem>
      <div className="border rounded-md">
        {editor && (
          <div className="flex flex-wrap p-2 border-b">
            <Toggle
              size="sm"
              pressed={editor.isActive("bold")}
              onPressedChange={() => editor.chain().focus().toggleBold().run()}
            >
              <Bold className="h-4 w-4" />
            </Toggle>
            <Toggle
              size="sm"
              pressed={editor.isActive("italic")}
              onPressedChange={() => editor.chain().focus().toggleItalic().run()}
            >
              <Italic className="h-4 w-4" />
            </Toggle>
            <Toggle
              size="sm"
              pressed={editor.isActive("strike")}
              onPressedChange={() => editor.chain().focus().toggleStrike().run()}
            >
              <Strikethrough className="h-4 w-4" />
            </Toggle>
            <Toggle
              size="sm"
              pressed={editor.isActive("bulletList")}
              onPressedChange={() => editor.chain().focus().toggleBulletList().run()}
            >
              <List className="h-4 w-4" />
            </Toggle>
            <Toggle
              size="sm"
              pressed={editor.isActive("orderedList")}
              onPressedChange={() => editor.chain().focus().toggleOrderedList().run()}
            >
              <ListOrdered className="h-4 w-4" />
            </Toggle>

            <Toggle size="sm" onPressedChange={() => editor.chain().focus().setHorizontalRule().run()}>
              <Minus className="h-4 w-4" />
            </Toggle>
            <Toggle size="sm" onPressedChange={() => editor.chain().focus().undo().run()}>
              <Undo className="h-4 w-4" />
            </Toggle>
            <Toggle size="sm" onPressedChange={() => editor.chain().focus().redo().run()}>
              <Redo className="h-4 w-4" />
            </Toggle>
          </div>
        )}
        <EditorContent editor={editor} className="p-2 min-h-[150px] border-0 focus-visible:border-0" />
      </div>
    </FormItem>
  );
};

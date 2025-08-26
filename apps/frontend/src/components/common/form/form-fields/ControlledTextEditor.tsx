import { useEffect } from "react";
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
    content: field.value as string,
    onUpdate: ({ editor }) => {
      field.onChange(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class:
          "tiptap outline-none focus:outline-none focus-visible:outline-none " +
          "border-0 focus:border-0 focus-visible:border-0 ring-0 focus:ring-0 focus-visible:ring-0",
        role: "textbox",
        "aria-label": "Rich text editor",
      },
    },
  });

  useEffect(() => {
    if (!editor) return;
    const incoming = (field.value as string) ?? "";

    // Avoid useless work / loops
    if (incoming === editor.getHTML()) return;

    if (incoming) {
      editor.commands.setContent(incoming, { emitUpdate: false });
    } else {
      editor.commands.clearContent(false);
    }
  }, [editor, field.value]);

  return (
    <FormItem className="focus-within:ring-0 focus-within:outline-none">
      <div className="border rounded-md focus-within:ring-0 focus-within:outline-none">
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
        <EditorContent editor={editor} className="p-2 min-h-[150px]" />
      </div>
    </FormItem>
  );
};

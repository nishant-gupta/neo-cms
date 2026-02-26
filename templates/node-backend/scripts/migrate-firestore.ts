import { Firestore, FieldValue } from "@google-cloud/firestore";

const projectId = process.env.GCP_PROJECT_ID;
const firestore = new Firestore(projectId ? { projectId } : {});
const collections = ["pages", "assets", "revisions"];

async function bootstrapCollections(): Promise<void> {
  for (const collectionName of collections) {
    const ref = firestore.collection(collectionName).doc("_meta");
    await ref.set(
      {
        bootstrap: true,
        updatedAt: FieldValue.serverTimestamp()
      },
      { merge: true }
    );

    process.stdout.write(`Bootstrapped collection: ${collectionName}\n`);
  }
}

async function run(): Promise<void> {
  try {
    await bootstrapCollections();
    process.stdout.write("Firestore migration completed.\n");
  } catch (error) {
    process.stderr.write(`Firestore migration failed: ${String(error)}\n`);
    process.exit(1);
  }
}

void run();

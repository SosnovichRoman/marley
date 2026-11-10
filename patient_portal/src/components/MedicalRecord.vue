<template>
	<div class="py-4 relative min-h-[75vh]">
		<div v-if="!loaded" class="min-h-[70vh]"></div>
		<div v-else-if="record" class="p-4 max-w-3xl space-y-6">
			<section class="rounded-xl border border-gray-200 bg-white p-4">
				<h2 class="text-lg font-semibold text-gray-900">{{ record.patient_name || "—" }}</h2>
				<p class="mt-1 text-xs text-gray-500"># {{ record.name }}</p>
				<dl class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
					<div>
						<dt class="text-gray-500">Gender</dt>
						<dd class="mt-1 font-medium text-gray-900">{{ record.sex || "—" }}</dd>
					</div>
					<div>
						<dt class="text-gray-500">Date of Birth</dt>
						<dd class="mt-1 font-medium text-gray-900">{{ formatDate(record.dob) }}</dd>
					</div>
					<div>
						<dt class="text-gray-500">Blood Group</dt>
						<dd class="mt-1 font-medium text-gray-900">{{ record.blood_group || "—" }}</dd>
					</div>
					<div>
						<dt class="text-gray-500">Mobile</dt>
						<dd class="mt-1 font-medium text-gray-900">{{ record.mobile || "—" }}</dd>
					</div>
					<div class="sm:col-span-2">
						<dt class="text-gray-500">Email</dt>
						<dd class="mt-1 font-medium text-gray-900">{{ record.email || "—" }}</dd>
					</div>
				</dl>
			</section>

			<section
				v-for="block in historyBlocks"
				:key="block.key"
				class="rounded-xl border border-gray-200 bg-white p-4"
			>
				<h3 class="text-gray-700 font-medium">{{ block.label }}</h3>
				<p class="mt-2 text-sm text-gray-800 whitespace-pre-wrap">
					{{ record[block.key] || "Not recorded" }}
				</p>
			</section>
		</div>

		<div v-else class="flex flex-col items-center justify-center min-h-[70vh] text-center p-6">
			<FeatherIcon name="file-text" class="w-12 h-12 text-gray-400 mb-3" />
			<h2 class="text-lg font-semibold text-gray-700">No Records Found</h2>
			<p class="text-sm text-gray-500">Your medical record is not available.</p>
		</div>
	</div>

	<Dialog :options="{
		title: dialog_title,
		message: dialog_message,
		size: 'xl',
		icon: { name: 'alert-triangle', appearance: 'warning' },
		actions: [{ label: 'OK', variant: 'solid' }],
	}" v-model="alert_dialog" @click="alert_dialog = false" />
</template>

<script setup>
import { ref } from 'vue'
import { createResource, Dialog } from 'frappe-ui'

const record = ref(null)
const loaded = ref(false)
const alert_dialog = ref(false)
const dialog_title = ref('')
const dialog_message = ref('')

const historyBlocks = [
	{ key: 'allergies', label: 'Allergies' },
	{ key: 'medication', label: 'Current Medication' },
	{ key: 'medical_history', label: 'Medical History' },
	{ key: 'surgical_history', label: 'Surgical History' },
]

const getRecord = createResource({
	url: '/api/method/healthcare.healthcare.api.patient_portal.get_medical_record',
	method: 'GET',
	onSuccess(response) {
		record.value = response || null
		loaded.value = true
	},
	onError(error) {
		loaded.value = true
		dialog_message.value = error.messages?.[0] || error
		dialog_title.value = 'Failed to load medical record'
		alert_dialog.value = true
	},
})
getRecord.fetch()

function formatDate(dateStr) {
	if (!dateStr) return '—'
	return new Date(dateStr).toLocaleDateString('en-IN', {
		year: 'numeric',
		month: 'long',
		day: 'numeric',
	})
}
</script>
